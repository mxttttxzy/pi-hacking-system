# Session 01 — Recon → Intercept → Replay → Defend

Your first hands-on session. You'll run the whole attack loop against the mock
robot on your own laptop, then close the hole and prove the attack fails. No
Raspberry Pis needed. About **60–90 minutes**.

> Everything here targets a mock target on your own machine. Same rule as the
> whole project: own the hardware, isolate the network, show the fix.

---

## Before you start

```bash
cd pi-hacking-system
pip install -r requirements.txt
./run-tests.sh          # should print ALL TESTS PASSED
```

You'll want **two terminals**: one to run the target, one to attack it. Install
`nmap` if you don't have it (`sudo apt install nmap`, or `brew install nmap`).

---

## Part 1 — Recon (find the target)

**Terminal A** — start the insecure mock robot:
```bash
python3 mock_robot.py
```
It prints `Mode: INSECURE (no auth)` and its URLs.

**Terminal B** — discover it and its open port:
```bash
nmap -sV -p 9000 127.0.0.1
```
✅ **Expected:** port `9000/tcp open`. That's the target's control service.
📝 **Record:** the nmap output. This is "an attacker sees the device announce itself."

---

## Part 2 — Intercept (watch with no login)

In a browser (or Terminal B), open the camera feed:
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

Now **replay** it a few times (up, down arrow, run again). Each one is accepted.
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

## Write it up

For each part, put in your report: what you did, the command, the result
(screenshot), the impact, and the fix. A finding without a fix is half a finding.

## Next session

- Session 02: the web attack — run OWASP Juice Shop (`practice-on-windows.md`) and land one SQL injection.
- Session 03: the AI demos — `prompt_inject_demo.py` and `adversarial_webcam.py`.
