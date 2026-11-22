# parrot-duet-syntax-test: calibrated permutation tests of warble-duet "syntax".
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Implements SYNTAX-PREREG.md. Input: data/calls.csv with columns duet, pair, pos, sex, type.

python syntax_test.py --data-dir data --out-dir out
"""
import argparse
import csv
import json
import os

import numpy as np

SEED = 20261122
WINDOW = 5
ALPHA_PRIMARY = 0.025
B_MAIN = 9999
N_WORLDS = 200
B_CAL = 499
THETA = 0.3
PRIORS = {"P1": 0.85, "P2": 0.65, "P3": 0.55, "P4": 0.35, "P5": 0.85, "P6": 0.55, "P7": 0.90}
P8 = {"SYNTAX_BEYOND_REPERTOIRE": 0.20, "ORDER_BEYOND_CONTENT": 0.35, "COOCCURRENCE_ONLY": 0.10,
      "EXPLAINED_BY_REPERTOIRE": 0.20, "UNDERPOWERED": 0.15}


# ---------------------------------------------------------------- corpus

def _norm_sex(s):
    s = (s or "").strip().upper()
    if s.startswith("F"):
        return "F"
    if s.startswith("M"):
        return "M"
    return "U"


def build_corpus(rows):
    """rows: list of dicts with keys duet, pair, pos, sex, type. Returns a dict of arrays sorted
    by (duet, pos). Blank type = uncategorised (-1). Blank pair everywhere = no pair id."""
    rows = list(rows)
    duet_names = sorted({str(r["duet"]) for r in rows})
    dmap = {d: i for i, d in enumerate(duet_names)}
    keyed = sorted(rows, key=lambda r: (dmap[str(r["duet"])], float(r["pos"])))
    types = sorted({str(r["type"]).strip() for r in keyed if str(r.get("type") or "").strip()})
    tmap = {t: i for i, t in enumerate(types)}
    pairs_raw = [str(r.get("pair") or "").strip() for r in keyed]
    has_pair = any(pairs_raw)
    # A duet's pair: its own value; blank pairs get a per-duet placeholder so they never pool.
    pnames = sorted({p for p in pairs_raw if p})
    pmap = {p: i for i, p in enumerate(pnames)}
    duet = np.array([dmap[str(r["duet"])] for r in keyed], dtype=np.int64)
    pair = np.array([pmap[p] if p else len(pnames) + duet[k] for k, p in enumerate(pairs_raw)],
                    dtype=np.int64)
    sexes = ["F", "M", "U"]
    sex = np.array([sexes.index(_norm_sex(r.get("sex"))) for r in keyed], dtype=np.int64)
    t = np.array([tmap[str(r["type"]).strip()] if str(r.get("type") or "").strip() else -1
                  for r in keyed], dtype=np.int64)
    return {"duet": duet, "pair": pair, "sex": sex, "t": t, "types": types,
            "n_duets": len(duet_names), "n_pairs": len(pnames), "has_pair": has_pair}


def read_calls(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- statistics

def adjacent_pairs(duet):
    i = np.flatnonzero(duet[1:] == duet[:-1])
    return i, i + 1


def window_pairs(duet, w=WINDOW):
    a, b = [], []
    n = duet.size
    for d in range(1, w + 1):
        if d >= n:
            break
        i = np.flatnonzero(duet[d:] == duet[:-d])
        a.append(i)
        b.append(i + d)
    if not a:
        e = np.zeros(0, dtype=np.int64)
        return e, e
    a = np.concatenate(a)
    b = np.concatenate(b)
    return np.concatenate([a, b]), np.concatenate([b, a])


def mi_bits(t, a, b, K):
    ta, tb = t[a], t[b]
    keep = (ta >= 0) & (tb >= 0)
    ta, tb = ta[keep], tb[keep]
    n = ta.size
    if n == 0:
        return 0.0
    c = np.bincount(ta * K + tb, minlength=K * K).reshape(K, K).astype(float)
    r = c.sum(axis=1)
    s = c.sum(axis=0)
    nz = c > 0
    return float((c[nz] / n * np.log2(c[nz] * n / np.outer(r, s)[nz])).sum())


def group_ids(C, null):
    nsex = 3
    if null == "N0":
        return np.zeros(C["t"].size, dtype=np.int64)
    if null == "N1":
        return C["sex"].copy()
    if null == "N2":
        return C["pair"] * nsex + C["sex"]
    if null == "N3":
        return C["duet"] * nsex + C["sex"]
    raise ValueError(null)


def permuter(t, g, rng):
    """Returns draw(): t with categorised labels permuted within groups g."""
    idx = np.flatnonzero(t >= 0)
    gs = g[idx]
    base = idx[np.argsort(gs, kind="stable")]

    def draw():
        order = idx[np.lexsort((rng.random(idx.size), gs))]
        out = t.copy()
        out[base] = t[order]
        return out
    return draw


def resampler(t, g, rng):
    """Returns draw(): each categorised slot redrawn with replacement from its group's labels."""
    idx = np.flatnonzero(t >= 0)
    gs = g[idx]
    o = np.argsort(gs, kind="stable")
    base = idx[o]
    _, start, size = np.unique(gs[o], return_index=True, return_counts=True)
    st = np.repeat(start, size)
    sz = np.repeat(size, size)

    def draw():
        pick = st + np.floor(rng.random(base.size) * sz).astype(np.int64)
        pick = np.minimum(pick, st + sz - 1)
        out = t.copy()
        out[base] = t[base[pick]]
        return out
    return draw


def perm_p(stat, t, draw, B):
    obs = stat(t)
    null = np.array([stat(draw()) for _ in range(B)])
    p = (1 + int(np.sum(null >= obs - 1e-12))) / (B + 1)
    return obs, p, null


def bh(p, q=0.05):
    p = np.asarray(p, dtype=float)
    m = p.size
    rej = np.zeros(m, dtype=bool)
    if m == 0:
        return rej
    o = np.argsort(p)
    passed = p[o] <= q * np.arange(1, m + 1) / m
    if passed.any():
        k = int(np.max(np.flatnonzero(passed))) + 1
        rej[o[:k]] = True
    return rej


def plant(t, a, b, sex, x, y, y_sex, theta, rng):
    out = t.copy()
    hit = (out[a] == x) & (sex[b] == y_sex) & (out[b] >= 0) & (rng.random(a.size) < theta)
    out[b[hit]] = y
    return out


# ---------------------------------------------------------------- analysis

def analyse(C, B=B_MAIN, n_worlds=N_WORLDS, b_cal=B_CAL, seed=SEED):
    rng = np.random.default_rng(seed)
    t, K = C["t"], max(len(C["types"]), 1)
    a1, b1 = adjacent_pairs(C["duet"])
    aw, bw = window_pairs(C["duet"])
    s_adj = lambda x: mi_bits(x, a1, b1, K)
    s_win = lambda x: mi_bits(x, aw, bw, K)
    res = {"n_duets": C["n_duets"], "n_pairs": C["n_pairs"], "has_pair": C["has_pair"],
           "n_calls": int(t.size), "n_categorised": int(np.sum(t >= 0)),
           "n_types_used": int(np.unique(t[t >= 0]).size), "window": WINDOW, "B": B,
           "seed": seed}
    if C["n_duets"] < 10 or res["n_categorised"] < 100:
        res["headline"] = "TOO_FEW_DATA"
        return res
    null_A = "N2" if C["has_pair"] else "N1"
    res["primary_A_null"] = null_A
    res["A_weak"] = not C["has_pair"]
    tests = {}
    for null in ("N0", "N1", "N2", "N3"):
        g = group_ids(C, null)
        for name, fn in (("S_adj", s_adj), ("S_win", s_win)):
            obs, p, nl = perm_p(fn, t, permuter(t, g, rng), B)
            tests[name + "@" + null] = {"obs": obs, "p": p, "null_mean": float(nl.mean()),
                                        "null_sd": float(nl.std())}
    res["tests"] = tests
    pA = tests["S_win@" + null_A]["p"]
    pB = tests["S_adj@N3"]["p"]
    res["p_A"], res["p_B"] = pA, pB

    # S2 rule counts
    ta, tb = t[a1], t[b1]
    keep = (ta >= 0) & (tb >= 0)
    obs_c = np.bincount(ta[keep] * K + tb[keep], minlength=K * K)
    cells = np.flatnonzero(obs_c >= 3)
    rules = {"cells": [[C["types"][c // K], C["types"][c % K], int(obs_c[c])] for c in cells]}
    for null in ("N0", "N2", "N3"):
        draw = permuter(t, group_ids(C, null), rng)
        sims = np.empty((B, cells.size))
        for k in range(B):
            x = draw()
            xa, xb = x[a1], x[b1]
            kk = (xa >= 0) & (xb >= 0)
            sims[k] = np.bincount(xa[kk] * K + xb[kk], minlength=K * K)[cells]
        mean = sims.mean(axis=0)
        dev = np.abs(obs_c[cells] - mean)
        p = (1 + np.sum(np.abs(sims - mean) >= dev - 1e-12, axis=0)) / (B + 1)
        rej = bh(p, 0.05)
        pos = rej & (obs_c[cells] > mean)
        rules[null] = {"null_mean": mean.tolist(), "p": p.tolist(), "bh": rej.tolist(),
                       "n_positive": int(pos.sum()), "n_negative": int((rej & ~pos).sum())}
    res["rules"] = rules

    # S3 self-repeats under N3 (two-sided around the null mean)
    rep = lambda x: float(np.mean(x[a1][keep] == x[b1][keep])) if keep.any() else 0.0
    draw3 = permuter(t, group_ids(C, "N3"), rng)
    rnull = np.array([rep(draw3()) for _ in range(B)])
    robs = rep(t)
    res["self_repeat"] = {"obs": robs, "null_mean": float(rnull.mean()),
                          "p_two_sided": (1 + int(np.sum(np.abs(rnull - rnull.mean())
                                                         >= abs(robs - rnull.mean()) - 1e-12)))
                          / (B + 1)}
    # S4 whole-duet repeats
    seqs = {}
    for d in range(C["n_duets"]):
        seqs.setdefault(tuple(t[C["duet"] == d].tolist()), []).append(d)
    res["duets_repeating_another"] = int(sum(len(v) for v in seqs.values() if len(v) > 1))

    # Calibration
    gW = group_ids(C, "N2" if C["has_pair"] else "N1")
    w0 = resampler(t, gW, rng)
    g0 = group_ids(C, "N0")
    gA = group_ids(C, null_A)
    g3 = group_ids(C, "N3")
    fa_adj = fa_win = sizeA = sizeB = 0
    for _ in range(n_worlds):
        x = w0()
        fa_adj += perm_p(s_adj, x, permuter(x, g0, rng), b_cal)[1] < 0.05
        fa_win += perm_p(s_win, x, permuter(x, g0, rng), b_cal)[1] < 0.05
        sizeA += perm_p(s_win, x, permuter(x, gA, rng), b_cal)[1] < ALPHA_PRIMARY
        sizeB += perm_p(s_adj, x, permuter(x, g3, rng), b_cal)[1] < ALPHA_PRIMARY
    cal = {"worlds": n_worlds, "B": b_cal, "naive_false_alarm_S_adj": fa_adj / n_worlds,
           "naive_false_alarm_S_win": fa_win / n_worlds, "size_A": sizeA / n_worlds,
           "size_B": sizeB / n_worlds}
    # W1 planted order: most frequent observed adjacent pair with x != y
    off = obs_c.reshape(K, K).copy()
    np.fill_diagonal(off, 0)
    if off.max() > 0:
        c = int(np.argmax(off))
        x, y = c // K, c % K
        sx = C["sex"][t == y]
        y_sex = int(np.bincount(sx, minlength=3).argmax())
        powB = 0
        for _ in range(n_worlds):
            z = plant(w0(), a1, b1, C["sex"], x, y, y_sex, THETA, rng)
            powB += perm_p(s_adj, z, permuter(z, g3, rng), b_cal)[1] < ALPHA_PRIMARY
        cal.update({"planted_x": C["types"][x], "planted_y": C["types"][y], "theta": THETA,
                    "power_B": powB / n_worlds})
    else:
        cal["power_B"] = 0.0
    res["calibration"] = cal

    if pA < ALPHA_PRIMARY and pB < ALPHA_PRIMARY:
        h = "SYNTAX_BEYOND_REPERTOIRE"
    elif pB < ALPHA_PRIMARY:
        h = "ORDER_BEYOND_CONTENT"
    elif pA < ALPHA_PRIMARY:
        h = "COOCCURRENCE_ONLY"
    elif cal["power_B"] >= 0.8:
        h = "EXPLAINED_BY_REPERTOIRE"
    else:
        h = "UNDERPOWERED"
    res["headline"] = h
    res["grading"] = grade(res)
    return res


def grade(res):
    cal = res["calibration"]
    out = {
        "P1": res["tests"]["S_adj@N0"]["p"] < 0.05,
        "P2": cal["naive_false_alarm_S_win"] >= 0.50,
        "P3": res["p_B"] < ALPHA_PRIMARY,
        "P4": res["p_A"] < ALPHA_PRIMARY,
        "P5": cal["size_A"] <= 0.05 and cal["size_B"] <= 0.05,
        "P6": cal["power_B"] >= 0.8,
        "P7": res["rules"]["N3"]["n_positive"] + res["rules"]["N3"]["n_negative"] < 20,
    }
    briers = {k: (PRIORS[k] - (1.0 if v else 0.0)) ** 2 for k, v in out.items()}
    p8 = sum((P8[k] - (1.0 if k == res["headline"] else 0.0)) ** 2 for k in P8)
    return {"outcomes": {k: bool(v) for k, v in out.items()}, "n_true": int(sum(out.values())),
            "brier_P1_P7": sum(briers.values()) / len(briers), "brier_P8": p8}


def write_results(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "syntax_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    L = ["# RESULTS-SYNTAX", "", "Headline: **%s**" % res["headline"], ""]
    L.append("Duets %d, pairs %d, calls %d (categorised %d), call types used %d."
             % (res["n_duets"], res["n_pairs"], res["n_calls"], res["n_categorised"],
                res["n_types_used"]))
    if "tests" in res:
        L += ["", "| statistic @ null | observed | null mean | p |", "|---|---|---|---|"]
        for k, v in res["tests"].items():
            L.append("| %s | %.4f | %.4f | %.4f |" % (k, v["obs"], v["null_mean"], v["p"]))
        L += ["", "Primary A (S_win @ %s): p = %.4f%s. Primary B (S_adj @ N3): p = %.4f."
              % (res["primary_A_null"], res["p_A"], " (A_WEAK: no pair id)" if res["A_weak"]
                 else "", res["p_B"])]
        L += ["", "Adjacent rules surviving BH q 0.05 (positive / negative):"]
        for n in ("N0", "N2", "N3"):
            L.append("- %s: %d / %d (of %d tested)" % (n, res["rules"][n]["n_positive"],
                     res["rules"][n]["n_negative"], len(res["rules"]["cells"])))
        c = res["calibration"]
        L += ["", "Calibration (%d worlds, B %d): naive false alarm S_adj %.3f, S_win %.3f; "
              "size A %.3f, size B %.3f; power B %.3f." % (c["worlds"], c["B"],
              c["naive_false_alarm_S_adj"], c["naive_false_alarm_S_win"], c["size_A"],
              c["size_B"], c["power_B"])]
        sr = res["self_repeat"]
        L.append("Self-repeats: %.4f observed vs %.4f under N3 (p %.4f). Duets repeating "
                 "another duet: %d." % (sr["obs"], sr["null_mean"], sr["p_two_sided"],
                                        res["duets_repeating_another"]))
        gr = res["grading"]
        L.append("Priors P1-P7: %d of 7 true, Brier %.3f; P8 Brier %.3f."
                 % (gr["n_true"], gr["brier_P1_P7"], gr["brier_P8"]))
    L += ["", "Made with AI agents working in MV2's name; not checked by a human expert.",
          "MV2, Munim, Inc., mv2@munimtech.com"]
    with open(os.path.join(out_dir, "RESULTS-SYNTAX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--B", type=int, default=B_MAIN)
    args = ap.parse_args()
    C = build_corpus(read_calls(os.path.join(args.data_dir, "calls.csv")))
    res = analyse(C, B=args.B)
    write_results(res, args.out_dir)
    print(res["headline"])


if __name__ == "__main__":
    main()
