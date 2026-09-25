# Start now — what you can build this week without the robots

You don't need the PiDog / PiSpider / PiCar to make real progress. Almost every
demo in the report can be **rehearsed on your laptop today**, then pointed at the
real robots later by changing one IP. Here's the order I'd do it in.

> Lab rule (still applies locally): everything here runs on your own machine /
> an isolated segment. Nothing points at the internet or a device you don't own.

---

## 1. Set up the attacker box (½ day)
- Install **Kali Linux** (live USB or a VM), or add the tools to your OS: `nmap`, `wireshark`, `hydra`, `sqlmap`, Burp Suite.
- Confirm they run. This is the same box you'll use on the real lab.

## 2. Practise the network + interception demo on a MOCK robot (1 evening)
This is the big one, and it mirrors the SunFounder robots closely.

1. Install Flask: `pip install flask`
2. Run the mock robot (sent alongside this file):
   ```
   python3 mock_robot.py
   ```
3. Do the full loop against it:
   - **Discover:** `nmap -sV -p 9000 127.0.0.1`
   - **Intercept (no auth):** open `http://127.0.0.1:9000/mjpg` — you reached the "camera" with no login.
   - **Capture + replay:** send `http://127.0.0.1:9000/cmd?move=forward`, capture it in Burp/Wireshark, then **replay** it — the mock "moves" with no controller.
4. Now **defend it:** add a password check to the `/cmd` route, re-run the replay, watch it fail. That before/after is your Demo C, rehearsed.

When the real robots arrive, the only change is `127.0.0.1` → the robot's IP.

## 3. Practise the web attack (1 evening)
- Run OWASP Juice Shop in Docker (see `practice-on-windows.md`).
- Get one **SQL injection** working, and one **XSS**. That's Demo D.

## 4. Prep the AI-era demos (no HAT+ needed yet — the HAT only accelerates)
- **Adversarial patch (Demo 1):** install a webcam image classifier on the laptop (e.g. a small pretrained model). Try to make it misclassify with a printed pattern. Start collecting/printing candidate patches now.
- **Prompt injection (Demo 2):** install **Ollama** and a small model on the laptop. Write a tiny "command parser" prompt ("turn this into a JSON motor command, never do X"), then try to break it with an injected instruction. This runs fine on the laptop; the HAT+ just makes it faster later.
- **Materials:** printer for patches, a couple of coloured stickers, a tape measure for the maze/track.

## 5. Paperwork (30 min, do it early)
- Get the **written authorization** line from your advisor.
- Draft the **report skeleton** from the main report doc so you're filling it in as you go, not at the end.

---

## What still needs the real robots
Only the *final* runs: the actual SunFounder camera stream, the real motors going
limp on an SSH takeover, and the AI HAT+ acceleration. Everything else — the
techniques, the scripts, the write-up — you can have finished before they arrive.

## Suggested first session (2–3 hours, tonight)
1. `pip install flask` → run `mock_robot.py`.
2. `nmap` it, open the feed, replay a command.
3. Add an auth check, prove the replay now fails.
4. Write that up using the defender's table in the report.

That single session already demonstrates the #1 and #2 IoT weaknesses end to end.
