# Project handoff — pi-hacking-system

Full context for this project, transferred from the session that set it up.
If you're picking this up in the dedicated `pi-hacking-system` session, start here.

## What this is

A closed-lab / sandbox security project for a comp-sci exhibit. You own
SunFounder robots (**PiDog, PiSpider, PiCar**) and a **Raspberry Pi AI HAT+**.
A laptop is the attacker; the robots are targets on an **isolated network** (no
internet), under **written authorization** from your advisor.

Theme: *devices are less secure than we think*, plus the evolution of hacking.
The rule throughout: **every demonstrated weakness is paired with its fix.**

## Repo state

Everything is built, linted (ruff clean), and self-tested. To verify this
checkout:

```bash
python3 -m pip install -r requirements.txt
./run-tests.sh          # should print: ALL TESTS PASSED
```

If `pip install` is refused ("externally-managed-environment"), use a venv —
see `docs/session-01.md`.

> If you ever see "11 pass / 3 fail", it just means the Python deps aren't
> installed yet (the mock_robot HTTP tests can't start Flask). Run the
> `pip install` above and they pass.

## What's in the repo

| File | What it does |
| --- | --- |
| `docs/session-01.md` | Step-by-step first lab: recon → intercept → replay → defend |
| `mock_robot.py` | Insecure practice target; `--token` demonstrates the fix |
| `ai_report.py` | nmap scan → findings (local Ollama AI, or offline rules) |
| `prompt_inject_demo.py` | Prompt-injection attack + the validator defence |
| `adversarial_patch_demo.py` | FGSM attack that fools a classifier (headless) |
| `adversarial_webcam.py` | The same attack live on a webcam (or `--image`) |
| `run-recon.sh` · `setup-target.sh` · `setup-ai-node.sh` · `lab-config.sh` | Pi setup + recon |
| `run-tests.sh` | Smoke-test everything |
| `attack-playbook.md` · `start-now.md` · `practice-on-windows.md` | Guides |

## Presentation deliverables (made alongside, still live)

- Project plan doc: https://claude.ai/code/artifact/5ff2e1fd-1538-44fa-ae57-153fcac75ba5
- Overview poster: https://claude.ai/artifact/5aY339hSSiNGm8rXnzvosF
- Animated build console (Claw'd mascot): https://claude.ai/artifact/WC3MU2XQckQEPgM4wf5Rne
- Full analysis & report doc: https://claude.ai/code/artifact/907a463d-1d3c-4bd2-a662-786456af996d
- Advisor slide deck: https://claude.ai/artifact/NrHLX9484f6NFfDAN4ubHL
- A tech-exhibit sheet was also filled out and delivered as a file.

## Lab-day preparation (done — ready for the Pis)

All the tooling for the live run is written and self-tested:

- `docs/session-02.md` — web attack lab (SQL-injection login bypass + sqlmap dump
  + parameterised-query fix).
- `docs/session-03.md` — AI-era demos on hardware (prompt injection + adversarial
  patch/webcam), each with its defence.
- `preflight.sh` — laptop-side readiness check: attacker tools, Python deps,
  isolation sanity, every Pi reachable, expected ports per role, Ollama on the AI
  node. Prints `READY` / `NOT READY`.
- `docs/demo-day-runbook.md` — the single go-live page: provision → isolate →
  pre-flight → run the four stations → teardown.

## What's next (open work)

1. Run it against the real Pis: follow `docs/demo-day-runbook.md` once the
   hardware arrives (`./preflight.sh` must print `READY` first).
2. Wire the AI demos to real hardware for demo day (webcam + the AI-node Ollama
   model / Hailo HAT+ acceleration).
3. Optional: a project write-up (design → build → evaluation) in `docs/`.

## Where things live

- Code: this repo, `mxttttxzy/pi-hacking-system`, branch `main`.
- Run order once the Pis arrive: `lab-config.sh` → `setup-target.sh` on each Pi
  → `setup-ai-node.sh` on the AI Pi → `run-recon.sh` from the laptop.
- Before the hardware arrives: everything is rehearsable on the laptop
  (`docs/session-01.md`, `mock_robot.py`, the demos).
