#!/usr/bin/env bash
#
# preflight.sh — "are we ready to run with the Pis?" check.
# Run this from the ATTACKER laptop, once the Pis are on the isolated switch.
#
#   ./preflight.sh              # full check: attacker tools + network + targets
#   ./preflight.sh --tools-only # just the laptop (no Pis needed yet)
#   ./preflight.sh --targets "192.168.50.11 192.168.50.12"   # override targets
#
# It never changes anything — it only looks and reports. Green across the board
# means you can start Session 02/03 and the live demos. Anything red is a thing
# to fix before demo day, not during it.
#
# run-tests.sh proves the toolkit's code works on a laptop; this proves the
# LIVE LAB is wired up and reachable. They are complementary.

set -uo pipefail
cd "$(dirname "$0")"
source ./lab-config.sh

# ---- args -------------------------------------------------------------------
TOOLS_ONLY=0
TARGETS_OVERRIDE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tools-only) TOOLS_ONLY=1 ;;
    --targets)    TARGETS_OVERRIDE="${2:-}"; shift ;;
    -h|--help)    grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1 (try --help)"; exit 2 ;;
  esac
  shift
done
TARGETS="${TARGETS_OVERRIDE:-$LAB_TARGETS}"

# ---- reporting helpers ------------------------------------------------------
pass=0; warn=0; fail=0
ok()   { echo "  [ OK ]  $*"; pass=$((pass+1)); }
note() { echo "  [WARN]  $*"; warn=$((warn+1)); }
bad()  { echo "  [FAIL]  $*"; fail=$((fail+1)); }
hdr()  { echo; echo "== $* =="; }

# Is a TCP port open on a host? Prefer nmap; fall back to bash /dev/tcp.
port_open() { # host port
  local host="$1" port="$2"
  if command -v nc >/dev/null 2>&1; then
    nc -z -w2 "$host" "$port" >/dev/null 2>&1
  else
    timeout 2 bash -c ">/dev/tcp/$host/$port" >/dev/null 2>&1
  fi
}
host_up() { ping -c1 -W1 "$1" >/dev/null 2>&1; }

# ---- 1. attacker tools ------------------------------------------------------
hdr "attacker laptop — required tools"
for t in nmap curl python3; do
  command -v "$t" >/dev/null 2>&1 && ok "$t present" || bad "$t MISSING (needed to run the lab)"
done

hdr "attacker laptop — attack tools (needed for the offensive demos)"
for t in sqlmap hydra; do
  command -v "$t" >/dev/null 2>&1 && ok "$t present" || bad "$t MISSING — install before Session 02/03"
done
for t in wireshark tshark burpsuite; do
  command -v "$t" >/dev/null 2>&1 && ok "$t present" || note "$t not on PATH (optional; used for capture/replay)"
done
command -v docker >/dev/null 2>&1 && ok "docker present (for local practice targets)" \
  || note "docker not found (only needed to run practice targets on the laptop)"

# ---- 2. python deps ---------------------------------------------------------
hdr "python deps for the demos"
if python3 -c "import flask, numpy" 2>/dev/null; then
  ok "flask + numpy importable"
else
  bad "python deps missing — run: python3 -m pip install -r requirements.txt (venv if pip is refused)"
fi
python3 -c "import cv2" 2>/dev/null && ok "opencv importable (webcam demo ready)" \
  || note "opencv not importable (adversarial_webcam needs it; the still-image path still works)"

# ---- 3. isolation sanity ----------------------------------------------------
hdr "network isolation (lab rule: no route to the internet)"
if ip route 2>/dev/null | grep -q '^default'; then
  note "a default route exists — on the isolated lab there should be NONE. Confirm you are on the lab switch, not your home network."
else
  ok "no default route (consistent with an isolated segment)"
fi

if [[ "$TOOLS_ONLY" -eq 1 ]]; then
  hdr "summary (tools-only)"; echo "  OK:$pass  WARN:$warn  FAIL:$fail"
  [[ $fail -eq 0 ]] && echo "  Laptop looks ready. Re-run without --tools-only once the Pis are on the switch." \
                    || echo "  Fix the FAILs above before demo day."
  exit $fail
fi

# ---- 4. targets reachable + expected services -------------------------------
hdr "lab targets — reachable on $LAB_SUBNET"
for ip in $TARGETS $IP_AI; do
  host_up "$ip" && ok "$ip responds to ping" || bad "$ip is NOT reachable (powered on? on the switch? IP set by setup-target.sh?)"
done

check_ports() { # label host "port:name port:name ..."
  local label="$1" host="$2"; shift 2
  host_up "$host" || { note "$label ($host) unreachable — skipping service check"; return; }
  for spec in "$@"; do
    local p="${spec%%:*}" name="${spec##*:}"
    port_open "$host" "$p" && ok "$label $host:$p ($name) open" \
                           || bad "$label $host:$p ($name) closed — did setup-target.sh finish for this role?"
  done
}

hdr "lab targets — expected services (matches setup-target.sh roles)"
check_ports "web"     "$IP_PI1" "3000:juice-shop" "80:dvwa"
check_ports "service" "$IP_PI2" "22:ssh" "21:ftp"
check_ports "network" "$IP_PI3" "80:apache" "445:samba"
check_ports "ai-node" "$IP_AI"  "11434:ollama"

# ---- summary ----------------------------------------------------------------
hdr "summary"
echo "  OK:$pass  WARN:$warn  FAIL:$fail"
if [[ $fail -eq 0 ]]; then
  echo "  READY — the lab is wired up. Proceed to docs/demo-day-runbook.md."
  exit 0
else
  echo "  NOT READY — resolve the FAILs above, then re-run. WARNs are usually fine."
  exit 1
fi
