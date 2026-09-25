#!/usr/bin/env python3
"""
adversarial_webcam.py — the adversarial attack, live on your webcam.

This is the interactive version of adversarial_patch_demo.py. It trains the same
tiny "sign" classifier, then reads your webcam and shows, in real time, how a
small crafted change to what the model sees flips its decision (STOP <-> GO).

It's a concept demo: the toy model effectively judges whether the top or bottom
of the view is brighter, so hold something light high vs low in frame to swing
it. The lesson is the same one that scales to a real vision model on the AI HAT+
— a tiny, deliberate perturbation changes the model's mind.

Run (on a laptop with a camera):
    python3 adversarial_webcam.py
      keys:  a = toggle the adversarial patch   q = quit

Test with a still image instead of a camera (works anywhere):
    python3 adversarial_webcam.py --image some.jpg

Needs:  pip install opencv-python numpy
"""

import argparse
import sys

try:
    import cv2
except ImportError:
    print("This demo needs OpenCV:  pip install opencv-python", file=sys.stderr)
    sys.exit(1)

# Reuse the model + attack from the headless demo so there's one source of truth.
# (This import also prints a friendly message and exits if numpy is missing.)
from adversarial_patch_demo import make_dataset, train, sigmoid, fgsm, SIZE


def frame_to_feature(frame):
    """Down-sample any camera frame to the model's 8x8 grayscale input."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (SIZE, SIZE)).astype("float64") / 255.0
    return small.flatten()


def classify(x, w, b):
    p = float(sigmoid(x @ w + b))
    return ("GO" if p >= 0.5 else "STOP"), p


def label_of(name, conf, color):
    return f"{name}  (GO={conf:.2f})", color


def run_image(path, w, b, epsilon):
    frame = cv2.imread(path)
    if frame is None:
        print(f"Could not read image: {path}", file=sys.stderr)
        return 1
    x = frame_to_feature(frame)
    c_label, c_p = classify(x, w, b)
    x_adv = fgsm(x, w, b, target_up=(c_label == "STOP"), epsilon=epsilon)
    a_label, a_p = classify(x_adv, w, b)
    print(f"Clean image      : {c_label}  (GO={c_p:.2f})")
    print(f"After adversarial: {a_label}  (GO={a_p:.2f})   [max pixel change {epsilon:.2f}]")
    if c_label != a_label:
        print(">> Flipped: a tiny perturbation changed the model's decision.")
    else:
        print(">> Not flipped — raise --epsilon and try again.")
    return 0


def run_camera(w, b, epsilon):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No camera found. Try:  python3 adversarial_webcam.py --image some.jpg",
              file=sys.stderr)
        return 1
    show_adv = False
    print("Camera running. Keys:  a = toggle adversarial patch,  q = quit")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        x = frame_to_feature(frame)
        c_label, c_p = classify(x, w, b)
        text, col = (f"model reads: {c_label}  (GO={c_p:.2f})", (60, 200, 90))
        if show_adv:
            x_adv = fgsm(x, w, b, target_up=(c_label == "STOP"), epsilon=epsilon)
            a_label, a_p = classify(x_adv, w, b)
            text = f"WITH PATCH -> {a_label}  (GO={a_p:.2f})"
            col = (70, 90, 240) if a_label != c_label else (60, 200, 90)
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, col, 2)
        cv2.putText(frame, "a: patch   q: quit", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.imshow("Adversarial webcam demo (SIMULATED / concept)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("a"):
            show_adv = not show_adv
    cap.release()
    cv2.destroyAllWindows()
    return 0


def main():
    ap = argparse.ArgumentParser(description="Adversarial attack, live on a webcam.")
    ap.add_argument("--image", help="classify a still image instead of the camera")
    ap.add_argument("--epsilon", type=float, default=0.12, help="patch strength (0-1)")
    args = ap.parse_args()

    X, y = make_dataset()
    w, b = train(X, y)

    if args.image:
        return run_image(args.image, w, b, args.epsilon)
    return run_camera(w, b, args.epsilon)


if __name__ == "__main__":
    sys.exit(main())
