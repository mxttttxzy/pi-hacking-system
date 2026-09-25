# Raspberry Pi Security Lab

A self-contained toolkit for a closed-lab security project: a laptop attacks
Raspberry Pis you own, on an isolated network, and an AI node helps both attack
and defend. Everything here can be **rehearsed on your laptop today** and pointed
at the real robots later by changing one IP.

> **The one rule:** only run this against hardware you own, on a network with no
> route to the internet or your real network, with written authorization. Every
> weakness you demonstrate should be paired with its fix.

---

## Quick start — run something now (no robots needed)

```bash
pip install -r requirements.txt

# 1. Turn a scan into a findings report (works offline)
python3 ai_report.py sample_scan.txt --no-ai

# 2. Run the insecure mock robot, then attack it from another terminal
python3 mock_robot.py
#   nmap -sV -p 9000 127.0.0.1
#   curl http://127.0.0.1:9000/mjpg               # camera, no login
#   curl "http://127.0.0.1:9000/cmd?move=forward" # command, no auth -> replay it

# 3. Prompt-injection attack + the validator that stops it
python3 prompt_inject_demo.py

# 4. Adversarial patch that flips STOP -> GO on a classifier
python3 adversarial_patch_demo.py

# 5. The same attack live on your webcam (needs a camera + opencv)
python3 adversarial_webcam.py            # or:  --image some.jpg

# Verify the whole toolkit at once
./run-tests.sh
```

## What's in here

| File | What it does |
| --- | --- |
| **README.md** | This file. |
| **requirements.txt** | Python deps for the demos. |
| **docs/session-01.md** | Step-by-step first lab session (recon → intercept → replay → defend). |
| **start-now.md** | The week-1 plan you can do without the robots. |
| **attack-playbook.md** | How to select, hack, and take control of a target — with fixes. |
| **practice-on-windows.md** | Run a real vulnerable target locally on Windows. |
| `lab-config.sh` | Shared IPs and subnet. Edit this first. |
| `setup-target.sh` | On each target Pi: static IP + Docker + vulnerable software. |
| `setup-ai-node.sh` | On the AI HAT+ Pi: install Ollama + a small local model. |
| `run-recon.sh` | From the laptop: scan the lab and run the report. |
| `ai_report.py` | Turn an nmap scan into findings (local AI, or offline rules). |
| `sample_scan.txt` | Example scan so `ai_report.py` runs today. |
| `mock_robot.py` | Deliberately-insecure stand-in for a SunFounder robot (`--token` shows the fix). |
| `prompt_inject_demo.py` | Prompt-injection attack **and** the defence. |
| `adversarial_patch_demo.py` | Real FGSM attack that fools an image classifier. |
| `adversarial_webcam.py` | The same attack live on a webcam (or a still image). |
| `run-tests.sh` | Smoke-test everything (linters + every demo). |

## The lab, in one line

```
Laptop (attacker) --> isolated switch --> Pi #1 · Pi #2 · Pi #3 · AI HAT+   (no internet)
```

## Order of operations, once the Pis arrive

1. Edit `lab-config.sh` if your IP range differs.
2. On each target Pi (while it still has internet): `sudo ./setup-target.sh web` (then `service`, `network`).
3. On the AI Pi: `sudo ./setup-ai-node.sh`.
4. Unplug from the internet, move everything to the isolated switch.
5. From the laptop: `./run-recon.sh`.

## Make the scripts executable

```bash
chmod +x *.sh
```
