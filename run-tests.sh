#!/usr/bin/env bash
#
# run-tests.sh — smoke-test the whole toolkit. No robots or camera needed.
# Checks shell syntax, that every Python file compiles, and that each demo's
# runnable path actually works (including the mock robot over HTTP).
#
#   ./run-tests.sh
#
# Needs the Python deps:  pip install -r requirements.txt

set -uo pipefail
cd "$(dirname "$0")"
fail=0
pass() { echo "PASS: $*"; }
bad()  { echo "FAIL: $*"; fail=1; }

echo "== shell syntax =="
for s in *.sh; do bash -n "$s" && pass "bash -n $s" || bad "bash -n $s"; done

echo "== python compiles =="
python3 -m py_compile ./*.py && pass "py_compile" || bad "py_compile"

echo "== demos =="
python3 ai_report.py sample_scan.txt --no-ai >/dev/null 2>&1 \
  && pass "ai_report" || bad "ai_report"

out="$(python3 prompt_inject_demo.py 2>&1)"
echo "$out" | grep -q "ALLOWED] robot will: forward" && pass "prompt_inject: benign allowed" || bad "prompt_inject: benign allowed"
echo "$out" | grep -q "BLOCKED" && pass "prompt_inject: injection blocked" || bad "prompt_inject: injection blocked"

# Capture output before grepping: piping straight into `grep -q` makes the demo
# see SIGPIPE, which `pipefail` would report as a failure of the whole pipeline.
aout="$(python3 adversarial_patch_demo.py 2>&1)"
echo "$aout" | grep -q "SUCCESS" \
  && pass "adversarial_patch: flips STOP->GO" || bad "adversarial_patch: flips STOP->GO"

echo "== webcam demo (optional, needs opencv) =="
if python3 -c "import cv2" 2>/dev/null; then
  python3 - <<'PY'
import numpy as np, cv2
img = np.full((120, 120, 3), 120, np.uint8)
img[:60, :, :] = 145          # top slightly brighter -> near-boundary scene
cv2.imwrite("/tmp/_awtest.png", img)
PY
  wout="$(python3 adversarial_webcam.py --image /tmp/_awtest.png 2>&1)"
  echo "$wout" | grep -q "Flipped" \
    && pass "adversarial_webcam: flips on image" || bad "adversarial_webcam: flips on image"
  rm -f /tmp/_awtest.png
else
  echo "SKIP: adversarial_webcam (opencv not installed)"
fi

echo "== mock robot over HTTP =="
python3 mock_robot.py --port 9199 >/dev/null 2>&1 &
pid=$!
resp="$(curl -s --retry-connrefused --retry 15 --retry-delay 1 "http://127.0.0.1:9199/cmd?move=left")"
echo "$resp" | grep -q '"ok":true' \
  && pass "mock_robot: insecure command accepted over HTTP" || bad "mock_robot: insecure command accepted over HTTP"
kill "$pid" 2>/dev/null || true

# Defended mode: a replay with no token must be rejected (403).
python3 mock_robot.py --port 9200 --token testtok >/dev/null 2>&1 &
pid=$!
code="$(curl -s -o /dev/null -w '%{http_code}' --retry-connrefused --retry 15 --retry-delay 1 "http://127.0.0.1:9200/cmd?move=left")"
[[ "$code" == "403" ]] \
  && pass "mock_robot: defended mode rejects tokenless replay (403)" || bad "mock_robot: defended mode rejects tokenless replay (got $code)"
kill "$pid" 2>/dev/null || true

echo
if [[ $fail -eq 0 ]]; then echo "ALL TESTS PASSED"; else echo "SOME TESTS FAILED"; fi
exit $fail
