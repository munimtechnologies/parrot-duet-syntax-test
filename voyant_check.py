# voyant_check.py: what the published "syntactic rules" statistic measures (SYNTAX-PREREG.md,
# AMENDMENT-1, secondary analyses T, R1, R2a, R2b).
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Dahlin et al. 2026 (J Avian Biol e03552) Table 1 lists the 'collocates' behind the reported
syntactic rules with Pearson r and p from the text tool Voyant. This script
 T   checks which number of observations n makes every published p match its r (numbers only);
 R1  tries to reproduce the r values: calls in file order as one text, split into 10 bins;
 R2a asks whether the rules survive shuffling call order inside every duet (order blindness);
 R2b counts 'rules' (p < 0.05 at n = 10) against random placement of whole duets.

python voyant_check.py --calls data/calls.csv --out-dir out/voyant
"""
import argparse
import csv
import json
import os

import numpy as np

SEED = 20261122
BINS = 10
N_SHUFFLE = 999
MIN_COUNT = 5
ALPHA = 0.05
ALIAS = {"CCall": "Contact Call"}
PRIORS = {"Q1_REPRODUCED": 0.45, "Q2_ORDER_BLIND": 0.90, "Q3_CHANCE_LEVEL": 0.55}

# Table 1 of the paper: term1, term2, r, p (None means "< 0.0001"), context 1, 3, 5 (None = blank)
TABLE1 = [
    ("Scree", "Scree", 1.000, None, 8, 46, 70),
    ("CCall", "CCall", 1.000, None, 6, 41, 71),
    ("Julia", "Julia", 1.000, None, 6, 30, 42),
    ("D", "D", 1.000, None, 2, 24, 42),
    ("B", "B", 1.000, None, 0, 10, 22),
    ("C", "C", 1.000, None, 0, 14, 28),
    ("M", "M", 1.000, None, 2, 18, 30),
    ("U1", "U1", 1.000, None, 3, 17, 29),
    ("U1", "U2", 0.986, None, 7, 21, 27),
    ("M", "Z", 0.874, 0.001, 0, 4, 11),
    ("B", "Ha", 0.859, 0.001, 0, 6, 7),
    ("C", "U1", 0.814, 0.004, 1, 2, 2),
    ("C", "O", 0.804, 0.005, 0, 2, 4),
    ("C", "U2", 0.784, 0.007, 0, 1, 3),
    ("J", "K", 0.746, 0.013, 0, 3, 6),
    ("Mirror M", "M", 0.740, 0.014, 2, 6, 11),
    ("Scree", "Yoohoo", 0.685, 0.029, 8, 21, 29),
    ("K", "M", 0.663, 0.037, 0, 5, 9),
    ("Mirror M", "Z", 0.642, 0.045, 3, 7, 15),
    ("Scree", "Z", -0.635, 0.049, None, None, None),
    ("B", "Mirror M", -0.638, 0.047, None, None, None),
    ("B", "U2", -0.641, 0.046, None, None, None),
    ("M", "Scree", -0.667, 0.035, None, None, None),
]


def tok(label):
    """Voyant-style single token: spaces removed, lower case."""
    return "".join(str(ALIAS.get(label, label)).split()).lower()


# ---------------------------------------------------------------- T: the published numbers

def p_from_r(r, n):
    """Two-sided p of Pearson r with n observations (t test, df = n - 2), exact closed forms
    (Abramowitz and Stegun 26.7.3-4, with sin(theta) = |r|). Works on scalars and arrays."""
    df = int(n) - 2
    if df < 1:
        raise ValueError("n must be >= 3")
    a = np.minimum(np.abs(np.asarray(r, dtype=float)), 1.0)
    s = 1.0 - a * a
    if df % 2 == 0:
        term = np.ones_like(a)
        total = np.ones_like(a)
        for k in range(1, df // 2):
            term = term * s * (2 * k - 1) / (2 * k)
            total = total + term
        A = a * total
    else:
        total = np.zeros_like(a)
        if df > 1:
            term = np.ones_like(a)
            total = np.ones_like(a)
            for k in range(1, (df - 1) // 2):
                term = term * s * (2 * k) / (2 * k + 1)
                total = total + term
        A = 2.0 / np.pi * (np.arcsin(a) + a * np.sqrt(s) * total)
    p = np.clip(1.0 - A, 0.0, 1.0)
    return float(p) if np.ndim(p) == 0 else p


def row_consistent(r_rep, p_rep, n):
    """Is the published p what r gives with n observations, allowing for 3-decimal rounding?"""
    lo = p_from_r(min(abs(r_rep) + 0.0005, 1.0), n)
    hi = p_from_r(max(abs(r_rep) - 0.0005, 0.0), n)
    if p_rep is None:
        return hi < 0.0001
    return lo - 0.0005 <= p_rep <= hi + 0.0005


def fitting_n(lo=3, hi=100):
    return [n for n in range(lo, hi + 1) if all(row_consistent(r[2], r[3], n) for r in TABLE1)]


# ---------------------------------------------------------------- the text Voyant saw

def load_stream(path, keep_unknown=True):
    """Calls in file order as tokens. Returns (codes, duet block ids, vocabulary)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: int(r["order"]))
    toks, blocks, names = [], [], {}
    for r in rows:
        if not (r.get("label") or "").strip():
            continue
        if not keep_unknown and not (r.get("type") or "").strip():
            continue
        toks.append(tok(r["label"].strip()))
        blocks.append(names.setdefault(r["duet"], len(names)))
    vocab = sorted(set(toks))
    vmap = {v: i for i, v in enumerate(vocab)}
    return (np.array([vmap[x] for x in toks], dtype=np.int64), np.array(blocks, dtype=np.int64),
            vocab)


def bin_freq(t, K, relative, bins=BINS):
    n = t.size
    b = (np.arange(n) * bins) // n
    M = np.zeros((bins, K))
    np.add.at(M, (b, t), 1.0)
    if relative:
        M = M / np.bincount(b, minlength=bins)[:, None]
    return M


def corr(M):
    Z = M - M.mean(axis=0)
    sd = np.sqrt((Z ** 2).sum(axis=0))
    with np.errstate(invalid="ignore", divide="ignore"):
        R = (Z.T @ Z) / np.outer(sd, sd)
    R[~np.isfinite(R)] = np.nan
    return R


def context_count(t, blocks, x, y, k, both=False, within=False):
    """Number of (x at i, y at j) with 1 <= j - i <= k (both: also y before x)."""
    n = t.size
    c = 0
    for d in range(1, k + 1):
        if d >= n:
            break
        a, b = t[:-d], t[d:]
        ok = np.ones(n - d, dtype=bool)
        if within:
            ok &= blocks[:-d] == blocks[d:]
        c += int(np.sum(ok & (a == x) & (b == y)))
        if both:
            c += int(np.sum(ok & (a == y) & (b == x)))
    return c


def within_shuffle(t, blocks, rng):
    """Random call order inside each duet; duets stay where they are."""
    return t[np.lexsort((rng.random(t.size), blocks))]


def placement_shuffle(t, blocks, rng):
    """Whole duets (with their own call order) put in a random order."""
    key = rng.permutation(int(blocks.max()) + 1)[blocks]
    return t[np.lexsort((np.arange(t.size), key))]


def rule_stats(t, K, relative, eligible):
    R = corr(bin_freq(t, K, relative))
    P = p_from_r(R, BINS)
    iu = np.triu_indices(K, 1)
    e = eligible[iu[0]] & eligible[iu[1]]
    with np.errstate(invalid="ignore"):
        sig = (P[iu] < ALPHA) & e
        pos = sig & (R[iu] > 0)
    return int(sig.sum()), int(pos.sum()), int(e.sum()), R, P


# ---------------------------------------------------------------- analysis

def analyse(path, n_shuffle=N_SHUFFLE, seed=SEED):
    rng = np.random.default_rng(seed)
    res = {"bins": BINS, "seed": seed, "n_shuffle": n_shuffle, "min_count": MIN_COUNT,
           "table1_rows": len(TABLE1),
           "table1_self_rows": sum(1 for r in TABLE1 if r[0] == r[1]),
           "table1_positive_rows": sum(1 for r in TABLE1 if r[2] > 0),
           "n_fitting_published_p": fitting_n()}
    nonself = [r for r in TABLE1 if r[0] != r[1]]

    # R1 reproduction of r, and of the context counts
    variants, context = {}, {}
    for keep in (True, False):
        base = "all" if keep else "noUnknown"
        t, blocks, vocab = load_stream(path, keep)
        vmap = {v: i for i, v in enumerate(vocab)}
        for rel in (False, True):
            R = corr(bin_freq(t, len(vocab), rel))
            rows, diffs = [], []
            for x, y, r, p, c1, c3, c5 in TABLE1:
                ro = None
                if tok(x) in vmap and tok(y) in vmap:
                    v = R[vmap[tok(x)], vmap[tok(y)]]
                    ro = float(v) if np.isfinite(v) else None
                rows.append({"term1": x, "term2": y, "r_paper": r, "r_ours": ro,
                             "p_ours": None if ro is None else p_from_r(ro, BINS)})
                if x != y and ro is not None:
                    diffs.append(abs(ro - r))
            variants[base + ("_rel" if rel else "_raw")] = {
                "rows": rows, "n_compared": len(diffs),
                "median_abs_diff": float(np.median(diffs)) if diffs else None,
                "max_abs_diff": float(np.max(diffs)) if diffs else None}
        for both in (False, True):
            for within in (False, True):
                cells = matched = 0
                detail = []
                for x, y, r, p, c1, c3, c5 in TABLE1:
                    if c1 is None:
                        continue
                    got = []
                    for k, pub in ((1, c1), (3, c3), (5, c5)):
                        g = None
                        if tok(x) in vmap and tok(y) in vmap:
                            g = context_count(t, blocks, vmap[tok(x)], vmap[tok(y)], k, both,
                                              within)
                        got.append(g)
                        cells += 1
                        matched += int(g == pub)
                    detail.append([x, y, got, [c1, c3, c5]])
                name = "%s_%s_%s" % (base, "both" if both else "right",
                                     "within" if within else "stream")
                context[name] = {"cells": cells, "matched": matched, "detail": detail}
    res["R1_variants"] = variants
    res["R1_context"] = context
    cand = [(v["median_abs_diff"], k) for k, v in variants.items()
            if v["median_abs_diff"] is not None]
    best = min(cand)[1] if cand else "all_raw"
    md = variants[best]["median_abs_diff"]
    res["R1_best_variant"] = best
    res["R1_reading"] = ("NOT_REPRODUCED" if md is None or md > 0.20 else
                         "REPRODUCED" if md <= 0.05 else "PARTLY_REPRODUCED")

    # R2 on the best variant
    keep = best.startswith("all")
    rel = best.endswith("_rel")
    t, blocks, vocab = load_stream(path, keep)
    K = len(vocab)
    vmap = {v: i for i, v in enumerate(vocab)}
    eligible = np.bincount(t, minlength=K) >= MIN_COUNT
    n_obs, n_pos_obs, n_tested, R0, P0 = rule_stats(t, K, rel, eligible)
    pairs = []
    for x, y, r, p, c1, c3, c5 in nonself:
        if tok(x) in vmap and tok(y) in vmap:
            i, j = vmap[tok(x)], vmap[tok(y)]
            sg = 1.0 if r > 0 else -1.0
            obs_sig = bool(np.isfinite(R0[i, j]) and P0[i, j] < ALPHA and R0[i, j] * sg > 0)
            pairs.append({"term1": x, "term2": y, "i": i, "j": j, "sign": sg,
                          "sig_in_file_order": obs_sig})
    hits_w = np.zeros(len(pairs))
    hits_p = np.zeros(len(pairs))
    dr_w = np.zeros(len(pairs))
    null_w, null_p = [], []
    for _ in range(n_shuffle):
        for kind in ("within", "place"):
            ts = (within_shuffle(t, blocks, rng) if kind == "within"
                  else placement_shuffle(t, blocks, rng))
            n_s, _, _, R, P = rule_stats(ts, K, rel, eligible)
            (null_w if kind == "within" else null_p).append(n_s)
            for q, pr in enumerate(pairs):
                i, j = pr["i"], pr["j"]
                ok = bool(np.isfinite(R[i, j]) and P[i, j] < ALPHA and R[i, j] * pr["sign"] > 0)
                if kind == "within":
                    hits_w[q] += ok
                    if np.isfinite(R[i, j]) and np.isfinite(R0[i, j]):
                        dr_w[q] += abs(R[i, j] - R0[i, j])
                else:
                    hits_p[q] += ok
    for q, pr in enumerate(pairs):
        pr["persist_within"] = hits_w[q] / n_shuffle
        pr["persist_placement"] = hits_p[q] / n_shuffle
        pr["mean_abs_dr_within"] = dr_w[q] / n_shuffle
        del pr["i"], pr["j"]
    sig_pairs = [pr for pr in pairs if pr["sig_in_file_order"]]
    pw = float(np.mean([pr["persist_within"] for pr in sig_pairs])) if sig_pairs else None
    pp = float(np.mean([pr["persist_placement"] for pr in sig_pairs])) if sig_pairs else None
    null_w, null_p = np.array(null_w), np.array(null_p)
    p_place = (1 + int(np.sum(null_p >= n_obs))) / (n_shuffle + 1)
    res["R2"] = {
        "variant": best, "n_tokens": int(t.size), "n_types": K,
        "n_eligible_types": int(eligible.sum()), "n_pairs_tested": n_tested,
        "rules_file_order": n_obs, "positive_rules_file_order": n_pos_obs,
        "expected_rules_if_independent": ALPHA * n_tested,
        "rules_within_shuffle_mean": float(null_w.mean()),
        "rules_placement_mean": float(null_p.mean()),
        "rules_placement_q05_q95": [float(np.quantile(null_p, 0.05)),
                                    float(np.quantile(null_p, 0.95))],
        "p_placement": p_place,
        "table_pairs": pairs, "n_table_pairs_sig_in_file_order": len(sig_pairs),
        "mean_persist_within": pw, "mean_persist_placement": pp}
    res["R2a_reading"] = ("NOT_APPLICABLE" if pw is None else
                          "ORDER_BLIND" if pw >= 0.80 else "ORDER_SENSITIVE")
    res["R2b_reading"] = "CHANCE_LEVEL" if p_place >= 0.05 else "EXCESS_AT_BIN_SCALE"
    out = {"Q1_REPRODUCED": res["R1_reading"] == "REPRODUCED",
           "Q2_ORDER_BLIND": res["R2a_reading"] == "ORDER_BLIND",
           "Q3_CHANCE_LEVEL": res["R2b_reading"] == "CHANCE_LEVEL"}
    res["grading"] = {"outcomes": out, "brier": float(np.mean(
        [(PRIORS[k] - (1.0 if v else 0.0)) ** 2 for k, v in out.items()]))}
    return res


def write_results(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "voyant_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    R2 = res["R2"]
    L = ["# RESULTS-VOYANT", "",
         "T: Table 1 has %d rows (%d pair a call type with itself, r = 1 by definition; %d "
         "positive). Numbers of observations n in 3-100 for which every published p equals the "
         "p of its r: %s." % (res["table1_rows"], res["table1_self_rows"],
                              res["table1_positive_rows"], res["n_fitting_published_p"]), "",
         "R1 (10 bins, file order): best variant %s, reading **%s**." % (
             res["R1_best_variant"], res["R1_reading"]), "",
         "| variant | rows compared | median abs diff r | max abs diff r |", "|---|---|---|---|"]
    for k, v in res["R1_variants"].items():
        L.append("| %s | %d | %s | %s |" % (k, v["n_compared"],
                 "NA" if v["median_abs_diff"] is None else "%.3f" % v["median_abs_diff"],
                 "NA" if v["max_abs_diff"] is None else "%.3f" % v["max_abs_diff"]))
    L += ["", "| context-count variant | published cells matched exactly |", "|---|---|"]
    for k, v in res["R1_context"].items():
        L.append("| %s | %d of %d |" % (k, v["matched"], v["cells"]))
    L += ["", "| term 1 | term 2 | r paper | r ours | p ours |", "|---|---|---|---|---|"]
    for row in res["R1_variants"][res["R1_best_variant"]]["rows"]:
        L.append("| %s | %s | %.3f | %s | %s |" % (
            row["term1"], row["term2"], row["r_paper"],
            "NA" if row["r_ours"] is None else "%.3f" % row["r_ours"],
            "NA" if row["p_ours"] is None else "%.4f" % row["p_ours"]))
    L += ["", "R2 (%s; %d tokens, %d types, %d with >= %d tokens; %d type pairs tested):" % (
        R2["variant"], R2["n_tokens"], R2["n_types"], R2["n_eligible_types"], res["min_count"],
        R2["n_pairs_tested"]),
        "- 'rules' (p < 0.05 at n = 10) in file order: %d (%d positive); %.1f expected if "
        "independent" % (R2["rules_file_order"], R2["positive_rules_file_order"],
                         R2["expected_rules_if_independent"]),
        "- mean rules after shuffling call order inside every duet: %.1f" %
        R2["rules_within_shuffle_mean"],
        "- mean rules under random placement of whole duets: %.1f (5-95%%: %.0f-%.0f); "
        "p_placement = %.3f, reading **%s**" % (
            R2["rules_placement_mean"], R2["rules_placement_q05_q95"][0],
            R2["rules_placement_q05_q95"][1], R2["p_placement"], res["R2b_reading"]),
        "- Table 1 pairs (different types) significant with the published sign in file order: "
        "%d of %d; mean share still significant after within-duet shuffles: %s, reading **%s**; "
        "after random placement: %s" % (
            R2["n_table_pairs_sig_in_file_order"], len(R2["table_pairs"]),
            "NA" if R2["mean_persist_within"] is None else "%.3f" % R2["mean_persist_within"],
            res["R2a_reading"],
            "NA" if R2["mean_persist_placement"] is None else "%.3f" %
            R2["mean_persist_placement"]),
        "", "Priors: %s; Brier %.3f." % (", ".join("%s %s" % (k, v) for k, v in
                                                   res["grading"]["outcomes"].items()),
                                        res["grading"]["brier"]),
        "", "Made with AI agents working in MV2's name; not checked by a human expert.",
        "MV2, Munim, Inc., mv2@munimtech.com"]
    with open(os.path.join(out_dir, "RESULTS-VOYANT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", default="data/calls.csv")
    ap.add_argument("--out-dir", default="out/voyant")
    ap.add_argument("--n-shuffle", type=int, default=N_SHUFFLE)
    args = ap.parse_args()
    res = analyse(args.calls, n_shuffle=args.n_shuffle)
    write_results(res, args.out_dir)
    print(res["R1_reading"], res["R2a_reading"], res["R2b_reading"])


if __name__ == "__main__":
    main()
