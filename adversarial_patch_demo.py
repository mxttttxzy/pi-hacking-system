#!/usr/bin/env python3
"""
adversarial_patch_demo.py — fool an image classifier with a tiny perturbation.

The scenario from the report: the robot's camera model recognises a "sign". An
attacker adds a small pattern (an adversarial patch) and the model misreads it —
without changing what the sign means to a human.

This is REAL adversarial machine learning (the FGSM attack) on a small classifier
you train on the spot, so it runs today with just numpy. The same idea scales to
the webcam + neural network you'll run on the AI HAT+ later; only the model gets
bigger, the attack is identical.

Run:
    python3 adversarial_patch_demo.py
    python3 adversarial_patch_demo.py --epsilon 0.12   # patch strength

Requires numpy (pip install numpy). Saves before/after images if Pillow is present.
"""

import argparse
import sys

try:
    import numpy as np
except ImportError:
    print("This demo needs numpy:  pip install numpy", file=sys.stderr)
    sys.exit(1)

SIZE = 8                      # 8x8 grayscale "signs"
N = 64                        # pixels per image
RNG = np.random.default_rng(0)


def make_dataset(n=400):
    """Two classes of 8x8 'signs': STOP (bright top) vs GO (bright bottom)."""
    X, y = [], []
    for _ in range(n):
        img = RNG.uniform(0.15, 0.55, N)          # brighter, noisier background
        if RNG.random() < 0.5:                     # STOP: top rows a little brighter
            img[:16] += RNG.uniform(0.12, 0.22)
            label = 0
        else:                                      # GO: bottom rows a little brighter
            img[-16:] += RNG.uniform(0.12, 0.22)
            label = 1
        X.append(np.clip(img, 0, 1)); y.append(label)
    return np.array(X), np.array(y)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def train(X, y, epochs=400, lr=0.5):
    """Plain logistic regression in numpy. Returns weights w, bias b."""
    w = np.zeros(N); b = 0.0
    for _ in range(epochs):
        p = sigmoid(X @ w + b)
        grad_w = X.T @ (p - y) / len(y)
        grad_b = float(np.mean(p - y))
        w -= lr * grad_w; b -= lr * grad_b
    return w, b


def predict(x, w, b):
    p = float(sigmoid(x @ w + b))
    return ("GO" if p >= 0.5 else "STOP"), p


def fgsm(x, w, b, target_up, epsilon):
    """Fast Gradient Sign Method: nudge every pixel by +/- epsilon in the
    direction that most increases the model's error. For a linear model the
    gradient of the score is just w, so this is one clean step."""
    direction = np.sign(w) if target_up else -np.sign(w)
    return np.clip(x + epsilon * direction, 0, 1)


def save_png(vec, path):
    try:
        from PIL import Image
    except ImportError:
        return False
    img = (vec.reshape(SIZE, SIZE) * 255).astype("uint8")
    Image.fromarray(img, mode="L").resize((256, 256), Image.NEAREST).save(path)
    return True


def ascii_art(vec):
    ramp = " .:-=+*#%@"
    out = []
    for r in range(SIZE):
        row = "".join(ramp[int(v * (len(ramp) - 1))] for v in vec[r*SIZE:(r+1)*SIZE])
        out.append("  " + row)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="FGSM adversarial-patch demo.")
    ap.add_argument("--epsilon", type=float, default=0.12,
                    help="patch strength (max change per pixel, 0-1)")
    args = ap.parse_args()

    X, y = make_dataset()
    w, b = train(X, y)
    acc = float(np.mean((sigmoid(X @ w + b) >= 0.5) == y))
    print(f"Trained a sign classifier. Clean accuracy: {acc*100:.1f}%\n")

    # Grab a STOP sign the model reads correctly.
    stops = X[y == 0]
    x = next(s for s in stops if predict(s, w, b)[0] == "STOP")
    label0, p0 = predict(x, w, b)

    # Attack: push it toward GO with the smallest patch we can.
    x_adv = fgsm(x, w, b, target_up=True, epsilon=args.epsilon)
    label1, p1 = predict(x_adv, w, b)
    linf = float(np.max(np.abs(x_adv - x)))

    print("=" * 56)
    print("  BEFORE the patch")
    print("=" * 56)
    print(ascii_art(x))
    print(f"\n  Model reads: {label0}  (confidence GO={p0:.2f})\n")

    print("=" * 56)
    print("  AFTER the patch")
    print("=" * 56)
    print(ascii_art(x_adv))
    print(f"\n  Model reads: {label1}  (confidence GO={p1:.2f})")
    print(f"  Largest change to any pixel: {linf:.2f}  (a faint patch)\n")

    if label0 != label1:
        print(">> SUCCESS: a small, deliberate pattern flipped STOP -> GO,")
        print("   without changing what the sign means to a person.")
    else:
        print(">> Not flipped yet — raise --epsilon (e.g. 0.2) and re-run.")

    a, bmp = save_png(x, "sign_clean.png"), save_png(x_adv, "sign_adversarial.png")
    if a and bmp:
        print("\nSaved sign_clean.png and sign_adversarial.png (upscaled).")
    else:
        print("\n(Install Pillow to also save PNGs: pip install pillow)")

    print("\nDefence: adversarial training (show the model these patched images")
    print("during training), input sanitising, and cross-checking the camera")
    print("against another sensor so one fooled model can't act alone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
