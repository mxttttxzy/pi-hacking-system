# Demo-day runbook — from boxes to a working lab

The single page to follow the day the Raspberry Pis arrive. It assumes you've
already rehearsed on the laptop (Sessions 01–03). Everything below is
copy-pasteable; the whole point is that lab day is *execution*, not improvisation.

> **The one rule, on the day too:** only against hardware you own, on a network
> with **no route to the internet or your real network**, with your advisor's
> **written authorization** in hand. Pair every weakness with its fix.

---

## 0. What you're building

```
Laptop (attacker, .10) --> isolated switch --> Pi#1 web (.11)
                                             ·  Pi#2 service (.12)
                                             ·  Pi#3 network (.13)
                                             ·  Pi#4 AI HAT+ (.20)     (NO internet)
```
IPs live in `lab-config.sh` — edit that one file if your range differs; every
script reads it.

---

## 1. Provision each Pi (while it still has internet)

Docker images, apt packages, Ollama and the model all download **now**, before
you isolate the network. Do this with each Pi on normal internet, then unplug.

**On each target Pi** (SSH in or use a keyboard), from a clone of this repo:
```bash
chmod +x *.sh
sudo ./setup-target.sh web        # Pi#1  -> Juice Shop :3000 + DVWA :80
sudo ./setup-target.sh service    # Pi#2  -> weak SSH (pi/raspberry) + anon FTP
sudo ./setup-target.sh network    # Pi#3  -> Apache :80 + open Samba :445
```
**On the AI Pi:**
```bash
sudo ./setup-ai-node.sh           # Pi#4  -> Ollama + llama3.2:1b, static IP .20
```
Each script sets the static lab IP with **no gateway** (so the Pi can't reach the
internet once moved) and prints what it deployed.

> If a Pi image has no `pi` user, `setup-target.sh service` tells you the one
> command to create it. If `pip`/apt is externally-managed anywhere, use a venv
> (see `docs/session-01.md`).

---

## 2. Isolate, then power up the lab

1. Unplug every Pi from the internet.
2. Connect the laptop + all Pis to the **isolated switch** only.
3. Set the laptop's static IP to `192.168.50.10/24`, **no gateway**.
4. Power on the Pis.

---

## 3. Pre-flight — verify the lab is wired up

From the laptop, before you demo anything:
```bash
./preflight.sh
```
It checks, and prints `[ OK ] / [WARN] / [FAIL]` for each:
- attacker tools present (`nmap`, `sqlmap`, `hydra`, `curl`, …) and Python deps,
- **no default route** (isolation sanity),
- every Pi answers on its IP,
- each target's expected ports are open (matches the `setup-target.sh` roles),
- the AI node's Ollama is listening (`:11434`).

**Do not proceed until it prints `READY`.** Every `[FAIL]` has a hint pointing at
the step that fixes it. `[WARN]`s (optional tools, missing camera) are usually
fine to demo without.

Sanity-check the toolkit code itself any time with:
```bash
./run-tests.sh          # ALL TESTS PASSED  (needs the Python deps)
```

---

## 4. The live sequence (recon → attack → fix, per station)

Run these in order — it's the same story escalating across three eras of hacking.

### Station A — Recon (all targets)
```bash
./run-recon.sh          # ping-sweep + service scan + AI findings report
```
Shows the whole lab lighting up and hands the scan to `ai_report.py`. This is your
opener: "the devices announce themselves."

### Station B — Classic IoT (Pi#1/#2/#3) → `docs/session-01.md`, `attack-playbook.md`
- Intercept + replay against the **service/network** targets (the real version of
  the mock-robot loop): open a no-auth endpoint, capture a request, replay it.
- SSH takeover of **Pi#2** with the default password, then `whoami` / `sudo -l`.
- **Fix shown:** require auth on control channels; delete default creds, SSH keys
  only; disable anonymous FTP.

### Station C — Web attack (Pi#1) → `docs/session-02.md`
- `' OR 1=1--` login bypass in Juice Shop, then `sqlmap` dumps the users table.
- **Fix shown:** parameterised queries — re-run the attack, it fails.

### Station D — AI-era attacks (laptop + Pi#4) → `docs/session-03.md`
- `prompt_inject_demo.py` against the AI node's model — the injection is
  `[BLOCKED]` by the validator.
- `adversarial_patch_demo.py` / `adversarial_webcam.py` — a faint patch flips
  STOP→GO.
- **Fix shown:** output validation + allow-list; adversarial training + sensor
  cross-checks.

Each station = **one weakness, landed, then closed.** That pairing is the exhibit.

---

## 5. Troubleshooting (fast)

| Symptom | First thing to check |
| --- | --- |
| `preflight` says a Pi is unreachable | Powered on? On the switch? Did `setup-target.sh` run and set the IP? `ping` it directly. |
| A target port is closed | `docker ps` on that Pi — the container may still be starting, or didn't pull before isolation. |
| Juice Shop slow to load | Give it ~30s after boot; confirm with the curl check in `session-02.md`. |
| `run-recon.sh` needs nmap | `sudo apt install nmap` on the laptop (it's required for recon). |
| AI demo "no model reachable" | The demo still runs via fallback; for the real run, confirm `:11434` on Pi#4 in `preflight`. |
| pip refused (externally-managed) | Use a venv — see `docs/session-01.md`. |

---

## 6. Teardown (leave nothing behind)

Part of the discipline — and part of the marks — is undoing what you did:
- Remove any persistence you added (SSH keys, cron jobs). You demonstrated it,
  now delete it.
- On each Pi: `docker rm -f <names>` to stop the vulnerable containers if you're
  reusing the hardware.
- Restore normal networking before the Pis go back on any real network.
- Keep the write-ups, screenshots, and the defender's tables — that's the
  deliverable.

---

## 7. Where everything is

| Need | File |
| --- | --- |
| IPs / subnet | `lab-config.sh` |
| Provision targets / AI node | `setup-target.sh`, `setup-ai-node.sh` |
| Readiness check | `preflight.sh` |
| Recon + report | `run-recon.sh`, `ai_report.py` |
| Session walk-throughs | `docs/session-01.md` · `02` · `03` |
| Attack reference | `attack-playbook.md` |
| Pre-hardware practice | `start-now.md`, `practice-on-windows.md` |
| Toolkit self-test | `run-tests.sh` |
| Full context / links | `HANDOFF.md` |
