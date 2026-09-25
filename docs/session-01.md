# Session 01 — Recon → Intercept → Replay → Defend

Your first hands-on session. You'll run the whole attack loop against the mock
robot on your own laptop, then close the hole and prove the attack fails. No
Raspberry Pis needed. About **60–90 minutes**.

> Everything here targets a mock target on your own machine. Same rule as the
> whole project: own the hardware, isolate the network, show the fix.

---

## Before you start

You need **Python 3** and **curl** (both are usually already installed). `nmap`
is *optional* — Part 1 gives a `curl` fallback if you don't have it.

Install the Python deps and run the self-test:
```bash
cd pi-hacking-system
python3 -m pip install -r requirements.txt
./run-tests.sh          # should end with: ALL TESTS PASSED
```

**If `pip install` is refused** with "externally-managed-environment" (common on
Linux/macOS), use a virtual environment:
```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt
```
(then run everything below inside that activated venv).

You'll want **two terminals**: one to run the target, one to attack it.

---

## Part 1 — Recon (find the target)

**Terminal A** — start the insecure mock robot:
```bash
python3 mock_robot.py
```
It prints `Mode: INSECURE (no auth)` and its URLs. Leave it running.

**Terminal B** — confirm the target is alive and find its open port.

Everyone has `curl`, so start with this — a reply means the service is up:
```bash
curl -s http://127.0.0.1:9000/ && echo "  <- target is up on port 9000"
```

Want the real port-scanner view? Use `nmap` if you have it (optional):
```bash
nmap -sV -p 9000 127.0.0.1          # if "command not found": skip it, or install nmap
```
- Install nmap later if you like: `sudo apt install nmap` (Linux) · `brew install nmap` (macOS) · [nmap.org/download](https://nmap.org/download.html) (Windows).

No nmap? You can still list the listening port with a built-in tool:
```bash
ss -tlnp 2>/dev/null | grep 9000 || netstat -an | grep 9000
```
✅ **Expected:** something shows port `9000` listening.
📝 **Record:** the output. This is "an attacker sees the device announce itself."

---

## Part 2 — Intercept (watch with no login)

Open the camera feed — in a browser go to `http://127.0.0.1:9000/mjpg`, or:
```bash
curl http://127.0.0.1:9000/mjpg
```
✅ **Expected:** the page says *"You reached the camera with no username or password."*
📝 **Record:** a screenshot. This is **OWASP IoT #2 — unencrypted, unauthenticated data**.

---

## Part 3 — Replay (puppet the device)

Send a movement command — notice there's no login:
```bash
curl "http://127.0.0.1:9000/cmd?move=forward"
```
✅ **Expected:** `{"auth_checked": false, "move": "forward", "ok": true}`, and Terminal A logs `command accepted (auth=NO)`.

Now **replay** it a few times (press up-arrow, Enter, repeat). Each one is accepted.
That's the attack: a captured request, replayed, controls the device.
📝 **Record:** Terminal A's log showing the commands piling up. This is **exposed, unauthenticated control**.

> Real version later: on the SunFounder robots you'd capture this request in
> Burp Suite or Wireshark instead of typing it, then replay it — and a real
> motor moves.

---

## Part 4 — Defend (close the hole)

Stop Terminal A (Ctrl-C) and restart it **with a required token** — the fix for
replay is to authenticate the control channel:
```bash
python3 mock_robot.py --token s3cr3t
```
It now prints `Mode: DEFENDED (token required)`.

**Re-run your replay from Part 3 (no token):**
```bash
curl -i "http://127.0.0.1:9000/cmd?move=forward"
```
✅ **Expected:** `HTTP/1.1 403 FORBIDDEN` and `{"error": "authentication required", "ok": false}`. The replay **fails**.

Only a request carrying the token works:
```bash
curl "http://127.0.0.1:9000/cmd?move=forward&token=s3cr3t"
```
✅ **Expected:** `ok: true` again.
📝 **Record:** the 403 before, the success after. This is your remediation, proven.

---

## What you just demonstrated

| Step | Weakness (OWASP IoT) | Fix you proved |
| --- | --- | --- |
| Recon | Exposed service | Only expose what's needed; isolate the segment |
| Intercept | Unencrypted, no-auth data | HTTPS + authentication |
| Replay | Unauthenticated control | Require an auth token on every command |

One 90-minute session covers three of the top IoT weaknesses **and** their
fixes — the exact story the report and the deck tell.

## If something doesn't work

- `./run-tests.sh` fails at the demos → the deps aren't installed; run the
  `pip install` (or venv) step above.
- `command not found: python3` → try `python` instead.
- `Address already in use` on port 9000 → an old server is still running; stop
  it (Ctrl-C in Terminal A) or use a different port: `python3 mock_robot.py --port 9001`
  (and change `9000` to `9001` in the curl commands).
- `nmap: command not found` → that step is optional; use the `curl` / `ss` lines instead.

## Write it up

For each part, put in your report: what you did, the command, the result
(screenshot), the impact, and the fix. A finding without a fix is half a finding.

## Next session

- Session 02: the web attack — run OWASP Juice Shop (`practice-on-windows.md`) and land one SQL injection.
- Session 03: the AI demos — `prompt_inject_demo.py` and `adversarial_webcam.py`.
