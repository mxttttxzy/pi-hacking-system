#!/usr/bin/env python3
"""
mock_robot.py — a deliberately-insecure stand-in for a stock SunFounder robot.

It mimics the parts that matter for the security demos, so you can practise the
whole recon -> intercept -> replay -> control loop on your OWN laptop today,
before the real PiDog / PiSpider / PiCar arrive. Nothing here is a real robot
and it only listens on your machine.

What it copies from the stock robots (on purpose, to be the "vulnerable" target):
  - an OPEN control port (default 9000)
  - a camera "feed" with NO authentication
  - movement commands accepted with NO authentication (so they can be replayed)

Run it:
    python3 mock_robot.py            # listens on http://127.0.0.1:9000
    python3 mock_robot.py --port 9000 --host 127.0.0.1

Then practise against it:
    nmap -sV -p 9000 127.0.0.1                 # discovery
    curl http://127.0.0.1:9000/mjpg            # view the "feed" with no login
    curl "http://127.0.0.1:9000/cmd?move=forward"   # send a command (no auth!)
    # capture that request in your browser / Burp, then REPLAY it -> robot "moves"

Only Flask is required:  pip install flask
"""

import argparse
import sys

try:
    from flask import Flask, request
except ImportError:
    print("This mock target needs Flask:  pip install flask", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
STATE = {"move": "stop", "commands_received": 0, "log": []}

# The "fix": when a token is set (via --token), the control endpoint requires it.
# Run without --token to show the insecure default; run WITH it to show the
# defended version, where a replayed command with no token is rejected.
TOKEN = None


@app.route("/")
def dashboard():
    return (
        "<h2>MockBot control panel (INSECURE DEMO)</h2>"
        "<p>No login required — that's the point.</p>"
        f"<p>Last move: <b>{STATE['move']}</b> · "
        f"commands received: {STATE['commands_received']}</p>"
        "<p>Feed: <a href='/mjpg'>/mjpg</a> · "
        "Command: <code>/cmd?move=forward</code></p>"
    )


@app.route("/mjpg")
def feed():
    # A real robot streams the camera here with no auth. We just prove the point:
    # anyone on the network can open this, no credentials asked.
    return (
        "<h3>LIVE CAMERA FEED (mock)</h3>"
        "<p>You reached the camera with no username or password.</p>"
        "<div style='width:320px;height:180px;background:#222;color:#0f0;"
        "font-family:monospace;display:flex;align-items:center;"
        "justify-content:center'>[ mock video frame ]</div>"
    )


@app.route("/cmd")
def cmd():
    # Insecure by default: no authentication, so a captured request can be replayed.
    # With --token set, the same replay (which carries no token) is rejected — the fix.
    if TOKEN is not None and request.args.get("token") != TOKEN:
        print("[MockBot] command REJECTED (bad/missing token)")
        return {"ok": False, "error": "authentication required"}, 403
    move = request.args.get("move", "stop")
    STATE["move"] = move
    STATE["commands_received"] += 1
    STATE["log"].append(move)
    auth = TOKEN is not None
    print(f"[MockBot] command accepted (auth={'yes' if auth else 'NO'}): move={move}  "
          f"(total {STATE['commands_received']})")
    return {"ok": True, "move": move, "auth_checked": auth}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Insecure mock robot for local security practice.")
    ap.add_argument("--host", default="127.0.0.1", help="bind address (keep it local)")
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--token", default=None,
                    help="require this token on /cmd (demonstrates the fix)")
    args = ap.parse_args()
    TOKEN = args.token
    mode = "DEFENDED (token required)" if TOKEN else "INSECURE (no auth)"
    print(f"MockBot listening — practise target only, localhost.  Mode: {mode}")
    print(f"  dashboard : http://{args.host}:{args.port}/")
    print(f"  feed      : http://{args.host}:{args.port}/mjpg")
    if TOKEN:
        print(f"  command   : http://{args.host}:{args.port}/cmd?move=forward&token={TOKEN}")
    else:
        print(f"  command   : http://{args.host}:{args.port}/cmd?move=forward   (no auth)")
    app.run(host=args.host, port=args.port)
