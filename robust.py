# robust.py: AMENDMENT-2 robustness checks of parrot-duet-syntax-test (secondary analyses).
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Implements AMENDMENT-2 of SYNTAX-PREREG.md, written after the registered primaries were graded.
None of these checks can change the registered headline; they say how far it can be trusted.

D  duplicates: drop every duet whose full call-type sequence repeats an earlier duet's; rerun A, B.
L  leave one pair out (and the unidentified duets as one unit); rerun A and B each time.
P  position-only null: types permuted only among calls of the same duet, sex and position class
   (first, middle, last of that sex in the duet); openers and closers stay where they are.
F  direction: S_adj restricted to female-then-male and to male-then-female neighbours, null N3.

python robust.py --calls data/calls.csv --out-dir out/robust
"""
import argparse
import json
import os
import sys

import numpy as np

try:
    import syntax_test as st
except ImportError:  # in the job the pinned engine is fetched into /out/src
    sys.path.insert(0, os.environ.get("SYNTAX_SRC", "/out/src"))
    import syntax_test as st

SEED = 20261124
ALPHA = 0.025
B_FULL = 9999
PRIORS = {"R1": 0.90, "R2": 0.70, "R3": 0.80, "R4": 0.50, "R5": 0.75, "R6": 0.55}


def primaries(rows, B, rng):
    """Registered primaries A (S_win under pair x sex) and B (S_adj under duet x sex)."""
    C = st.build_corpus(rows)
    t, K = C["t"], max(len(C["types"]), 1)
    a1, b1 = st.adjacent_pairs(C["duet"])
    aw, bw = st.window_pairs(C["duet"])
    gA = st.group_ids(C, "N2" if C["has_pair"] else "N1")
    g3 = st.group_ids(C, "N3")
    oA, pA, _ = st.perm_p(lambda x: st.mi_bits(x, aw, bw, K), t, st.permuter(t, gA, rng), B)
    oB, pB, _ = st.perm_p(lambda x: st.mi_bits(x, a1, b1, K), t, st.permuter(t, g3, rng), B)
    return {"n_duets": int(C["n_duets"]), "n_calls": int(t.size), "S_win": float(oA),
            "p_A": float(pA), "S_adj": float(oB), "p_B": float(pB)}


def dedup_rows(rows):
    """Drops every duet whose call-type sequence equals an earlier duet's (build_corpus order)."""
    C = st.build_corpus(rows)
    names = sorted({str(r["duet"]) for r in rows})
    seen = set()
    drop = []
    for d in range(C["n_duets"]):
        key = tuple(C["t"][C["duet"] == d].tolist())
        if key in seen:
            drop.append(names[d])
        else:
            seen.add(key)
    dset = set(drop)
    return [r for r in rows if str(r["duet"]) not in dset], sorted(drop)


def lopo(rows, B, rng):
    out = []
    for P in sorted({(r.get("pair") or "").strip() for r in rows}):
        sub = [r for r in rows if (r.get("pair") or "").strip() != P]
        res = primaries(sub, B, rng)
        res["left_out"] = P if P else "(unidentified)"
        res["n_calls_left_out"] = len(rows) - len(sub)
        out.append(res)
    return out


def position_groups(C):
    """Group id = duet x sex x position class (0 first, 1 middle, 2 last of that sex in the duet).
    A sex with one call in a duet is class 0. Arrays of C are sorted by (duet, pos)."""
    key = C["duet"] * 3 + C["sex"]
    cls = np.zeros(key.size, dtype=np.int64)
    for k in np.unique(key):
        idx = np.flatnonzero(key == k)
        if idx.size >= 2:
            cls[idx[1:-1]] = 1
            cls[idx[-1]] = 2
    return key * 3 + cls


def position_test(C, B, rng):
    t, K = C["t"], max(len(C["types"]), 1)
    a1, b1 = st.adjacent_pairs(C["duet"])
    g = position_groups(C)
    obs, p, nl = st.perm_p(lambda x: st.mi_bits(x, a1, b1, K), t, st.permuter(t, g, rng), B)
    idx = np.flatnonzero(t >= 0)
    _, cnt = np.unique(g[idx], return_counts=True)
    return {"obs": float(obs), "null_mean": float(nl.mean()), "p": float(p),
            "n_slots_permutable": int(cnt[cnt >= 2].sum())}


def direction(C, B, rng):
    t, K, sex = C["t"], max(len(C["types"]), 1), C["sex"]
    a1, b1 = st.adjacent_pairs(C["duet"])
    g3 = st.group_ids(C, "N3")
    out = {}
    for name, sa, sb in (("F_to_M", 0, 1), ("M_to_F", 1, 0)):
        m = (sex[a1] == sa) & (sex[b1] == sb)
        a, b = a1[m], b1[m]
        obs, p, nl = st.perm_p(lambda x: st.mi_bits(x, a, b, K), t, st.permuter(t, g3, rng), B)
        out[name] = {"n_neighbour_pairs": int(m.sum()), "obs": float(obs),
                     "null_mean": float(nl.mean()), "p": float(p)}
    return out


def readings(res):
    r = {}
    d = res["dedup"]
    r["dedup"] = "ROBUST" if d["p_A"] < ALPHA and d["p_B"] < ALPHA else "NOT_ROBUST"
    for key, lab in (("p_B", "lopo_B"), ("p_A", "lopo_A")):
        bad = [x["left_out"] for x in res["lopo"] if x[key] >= ALPHA]
        r[lab] = "ROBUST" if not bad else "DEPENDS_ON:" + ",".join(bad)
    r["position"] = ("TRANSITIONS_BEYOND_POSITION" if res["position"]["p"] < ALPHA
                     else "POSITION_MAY_EXPLAIN")
    fm = res["direction"]["F_to_M"]["p"] < ALPHA
    mf = res["direction"]["M_to_F"]["p"] < ALPHA
    r["direction"] = ("BOTH" if fm and mf else "F_TO_M_ONLY" if fm
                      else "M_TO_F_ONLY" if mf else "NEITHER")
    return r


def grade(res):
    out = {"R1": res["dedup"]["p_B"] < ALPHA,
           "R2": all(x["p_B"] < ALPHA for x in res["lopo"]),
           "R3": all(x["p_A"] < ALPHA for x in res["lopo"]),
           "R4": res["position"]["p"] < ALPHA,
           "R5": res["direction"]["F_to_M"]["p"] < ALPHA,
           "R6": res["direction"]["M_to_F"]["p"] < ALPHA}
    brier = sum((PRIORS[k] - (1.0 if v else 0.0)) ** 2 for k, v in out.items()) / len(out)
    return {"outcomes": {k: bool(v) for k, v in out.items()}, "brier": brier}


def run(rows, B=B_FULL, seed=SEED):
    rng = np.random.default_rng(seed)
    rows = list(rows)
    C = st.build_corpus(rows)
    res = {"seed": seed, "B": B, "alpha": ALPHA, "n_duets": int(C["n_duets"]),
           "n_calls": int(C["t"].size)}
    kept, dropped = dedup_rows(rows)
    res["dedup"] = primaries(kept, B, rng)
    res["dedup"]["dropped_duets"] = dropped
    res["lopo"] = lopo(rows, B, rng)
    res["position"] = position_test(C, B, rng)
    res["direction"] = direction(C, B, rng)
    res["readings"] = readings(res)
    res["grading"] = grade(res)
    return res


def write(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "robust_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    d, rd = res["dedup"], res["readings"]
    L = ["# RESULTS-ROBUST (AMENDMENT-2, secondary)", "",
         "Duets %d, calls %d, B %d, alpha %.3f, seed %d." % (res["n_duets"], res["n_calls"],
                                                           res["B"], res["alpha"], res["seed"]),
         "", "D duplicates: dropped %d duets (%s); A p %.4f, B p %.4f: **%s**."
         % (len(d["dropped_duets"]), ", ".join(d["dropped_duets"]) or "none", d["p_A"],
            d["p_B"], rd["dedup"]),
         "", "L leave one pair out:", "", "| left out | calls removed | A p | B p |",
         "|---|---|---|---|"]
    for x in res["lopo"]:
        L.append("| %s | %d | %.4f | %.4f |" % (x["left_out"], x["n_calls_left_out"],
                                                x["p_A"], x["p_B"]))
    L += ["", "B: **%s**. A: **%s**." % (rd["lopo_B"], rd["lopo_A"])]
    p = res["position"]
    L += ["", "P position-only null: S_adj %.4f against %.4f, p %.4f (%d permutable calls): "
          "**%s**." % (p["obs"], p["null_mean"], p["p"], p["n_slots_permutable"],
                       rd["position"])]
    for k in ("F_to_M", "M_to_F"):
        v = res["direction"][k]
        L.append("F %s: %d neighbour pairs, MI %.4f against %.4f, p %.4f."
                 % (k, v["n_neighbour_pairs"], v["obs"], v["null_mean"], v["p"]))
    L += ["Direction: **%s**." % rd["direction"], "",
          "Priors R1-R6 Brier %.3f; outcomes %s." % (res["grading"]["brier"],
                                                    json.dumps(res["grading"]["outcomes"])),
          "", "Made with AI agents working in MV2's name; not checked by a human expert.",
          "MV2, Munim, Inc., mv2@munimtech.com"]
    with open(os.path.join(out_dir, "RESULTS-ROBUST.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--B", type=int, default=B_FULL)
    args = ap.parse_args()
    res = run(st.read_calls(args.calls), B=args.B)
    write(res, args.out_dir)
    print(json.dumps(res["readings"]))


if __name__ == "__main__":
    main()
