"""
Review helper — for later use, once you're ready to build the retraining loop.

Walks through captured samples that don't yet have a verified_label, shows
the image + the model's own decision, and lets you confirm or correct it.
Only samples with a verified_label are eligible for training
(see db.get_training_ready_samples).

Usage (from backend/ directory, with venv active):
    python -m review_tools.review_samples
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import get_unverified_samples, set_verified_label  # noqa: E402


def main():
    samples = get_unverified_samples(limit=20)
    if not samples:
        print("No unverified samples found.")
        return

    print(f"{len(samples)} sample(s) awaiting review.\n")
    for s in samples:
        print(f"[id={s['id']}] session={s['session_id']}")
        print(f"  image: {s['image_path']}")
        print(f"  model decision: {s['decision']}  (fusion_score={s['fusion_score']})")
        answer = input("  Verified label? [r]eal / [s]poof / [skip]: ").strip().lower()

        if answer in ("r", "real"):
            set_verified_label(s["id"], "real")
            print("  -> marked REAL\n")
        elif answer in ("s", "spoof"):
            set_verified_label(s["id"], "spoof")
            print("  -> marked SPOOF\n")
        else:
            print("  -> skipped\n")


if __name__ == "__main__":
    main()