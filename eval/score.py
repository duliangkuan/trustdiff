#!/usr/bin/env python3
"""Score trustdiff eval runs.

Compares eval/results/caseNN.json (reviewer agent output) against
eval/truth/caseNN.json (ground truth).

A drift case counts as DETECTED when verdict == "drift" AND at least one
ground-truth category appears among the findings' categories.
A clean case counts as FALSE POSITIVE when verdict == "drift".

Usage:
  python eval/score.py                                   # default truth/ vs results/
  python eval/score.py --truth truth_scale --results results_scale
  python eval/score.py --drift-verdict block             # score a control arm
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", default="truth", help="truth dir name under eval/")
    ap.add_argument("--results", default="results", help="results dir name under eval/")
    ap.add_argument("--drift-verdict", default="drift",
                    help="verdict string meaning drift (use 'block' for control arms)")
    args = ap.parse_args()
    truth_dir = os.path.join(HERE, args.truth)
    results_dir = os.path.join(HERE, args.results)
    drift_word = args.drift_verdict

    if not os.path.isdir(truth_dir):
        print("no truth dir at %s" % truth_dir)
        sys.exit(1)
    rows = []
    detected = missed = fp = tn = no_result = 0
    for fn in sorted(os.listdir(truth_dir)):
        if not fn.endswith(".json"):
            continue
        case = fn[:-5]
        truth = load(os.path.join(truth_dir, fn))
        rpath = os.path.join(results_dir, fn)
        if not os.path.exists(rpath):
            rows.append((case, truth["drift"], "-", "NO RESULT", ""))
            no_result += 1
            continue
        try:
            res = load(rpath)
        except (json.JSONDecodeError, OSError) as e:
            rows.append((case, truth["drift"], "-", "BAD JSON: %s" % e, ""))
            no_result += 1
            continue
        verdict = res.get("verdict", "?")
        found_cats = sorted({f.get("category", "?")
                             for f in res.get("findings", [])})
        if truth["drift"]:
            cat_hit = bool(set(truth["categories"]) & set(found_cats))
            if verdict == drift_word and cat_hit:
                status, detected = "DETECTED", detected + 1
            elif verdict == drift_word:
                status, detected = "FLAGGED (wrong category)", detected + 1
            else:
                status, missed = "MISSED", missed + 1
        else:
            if verdict == drift_word:
                status, fp = "FALSE POSITIVE", fp + 1
            else:
                status, tn = "clean pass", tn + 1
        rows.append((case, truth["drift"], verdict, status,
                     ",".join(found_cats)))

    w = (8, 7, 8, 24, 40)
    hdr = ("case", "drift?", "verdict", "status", "found categories")
    line = "  ".join(h.ljust(wd) for h, wd in zip(hdr, w))
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(str(c).ljust(wd) for c, wd in zip(r, w)))

    n_drift = detected + missed
    n_clean = fp + tn
    print()
    if n_drift:
        print("detection rate : %d/%d = %.0f%%  (target >= 80%%)"
              % (detected, n_drift, 100.0 * detected / n_drift))
    if n_clean:
        print("false positives: %d/%d = %.0f%%  (target <= 15%%, i.e. 0/4)"
              % (fp, n_clean, 100.0 * fp / n_clean))
    if no_result:
        print("unscored cases : %d" % no_result)
    ok = n_drift and detected / n_drift >= 0.8 and (not n_clean or fp / n_clean <= 0.15)
    print("\nOVERALL: %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
