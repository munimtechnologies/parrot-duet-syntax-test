# convert.py: Dryad sheet (CSV dump of Supplement_Data_DRYAD.xlsx) -> calls.csv for syntax_test.py
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Implements the converter rules of SYNTAX-PREREG.md (AMENDMENT-1). Standard library only.

python convert.py <dryad_sheet01.csv> <out_dir>
writes <out_dir>/calls.csv (pair code 'U' read as an unidentified pair -> blank) and
<out_dir>/upair/calls.csv (sensitivity: 'U' kept as one pair), and prints a JSON summary.
"""
import csv
import hashlib
import json
import os
import sys

UNKNOWN_LABELS = {"unknown"}
UNIDENTIFIED_PAIRS = {"U"}
COLS = {"duet": "Duet Name", "pair": "Pair", "pos": "Note #", "type": "Call Type",
        "sex": "Sex (M,F,U)"}
# Published per-type counts (Dahlin et al. 2026, Fig. 3), keyed by label without spaces, lower case.
FIG3 = {"alien": 6, "ha": 5, "mirrorm": 15, "nert": 4, "q": 7, "yoohoo": 11, "x": 5,
        "accordion": 8, "breeze": 7, "u2": 10, "b": 24, "jfancy": 13, "r": 18, "contactcall": 29,
        "dippy": 7, "hook": 7, "julia": 24, "zert": 4, "d": 33, "k": 14, "c": 27, "p": 7, "m": 24,
        "f": 8, "christine": 8, "j": 15, "o": 17, "z": 15, "u1": 10, "sauron": 6, "scree": 41,
        "n": 7, "flert": 5, "hoo": 6, "mirrorf": 6, "shortcontactcall": 8}
OUT_FIELDS = ["order", "duet", "pair", "pos", "sex", "type", "label"]


def norm(s):
    """Strip and collapse internal whitespace."""
    return " ".join(str("" if s is None else s).split())


def key(label):
    return "".join(norm(label).split()).lower()


def find_columns(header):
    found = {}
    for k, want in COLS.items():
        for h in header:
            if norm(h).lower() == want.lower():
                found[k] = h
                break
        if k not in found:
            raise KeyError("column not found: %s" % want)
    return found


def convert(rows, u_as_pair=False):
    """rows: list of dicts from csv.DictReader of the Dryad sheet. Returns (calls, anomalies)."""
    if not rows:
        return [], ["no rows"]
    col = find_columns(list(rows[0].keys()))
    calls, anomalies = [], []
    seen, current, expect = set(), None, 1
    for i, r in enumerate(rows):
        duet = norm(r[col["duet"]])
        if not duet:
            anomalies.append("row %d: blank duet name" % (i + 2))
            continue
        if duet != current:
            if duet in seen:
                anomalies.append("row %d: duet %s is not contiguous" % (i + 2, duet))
            seen.add(duet)
            current, expect = duet, 1
        pos_raw = norm(r[col["pos"]])
        try:
            pos = int(float(pos_raw))
        except ValueError:
            anomalies.append("row %d: bad Note # %r" % (i + 2, pos_raw))
            pos = expect
        if pos != expect:
            anomalies.append("row %d: duet %s note %d, expected %d" % (i + 2, duet, pos, expect))
        expect = pos + 1
        label = norm(r[col["type"]])
        typ = "" if label.lower() in UNKNOWN_LABELS else label
        sex = norm(r[col["sex"]]).upper()
        sex = sex if sex in ("F", "M") else "U"
        pair = norm(r[col["pair"]])
        if pair in UNIDENTIFIED_PAIRS and not u_as_pair:
            pair = ""
        calls.append({"order": i, "duet": duet, "pair": pair, "pos": pos, "sex": sex,
                      "type": typ, "label": label})
    return calls, anomalies


def summarise(calls):
    duets = []
    for c in calls:
        if not duets or duets[-1] != c["duet"]:
            duets.append(c["duet"])
    counts_all, counts_sexed = {}, {}
    for c in calls:
        if c["type"]:
            k = key(c["type"])
            counts_all[k] = counts_all.get(k, 0) + 1
            if c["sex"] in ("F", "M"):
                counts_sexed[k] = counts_sexed.get(k, 0) + 1
    fig3 = {k: {"paper": v, "all": counts_all.get(k, 0), "sexed": counts_sexed.get(k, 0)}
            for k, v in FIG3.items()}
    extra = sorted(set(counts_all) - set(FIG3))
    return {"n_calls": len(calls), "n_duets": len(duets),
            "n_unknown": sum(1 for c in calls if not c["type"]),
            "pairs": sorted({c["pair"] for c in calls}),
            "n_types": len(counts_all), "labels_not_in_fig3": extra,
            "fig3_match_all": sum(1 for v in fig3.values() if v["paper"] == v["all"]),
            "fig3_match_sexed": sum(1 for v in fig3.values() if v["paper"] == v["sexed"]),
            "fig3": fig3, "sex_counts": {s: sum(1 for c in calls if c["sex"] == s)
                                         for s in ("F", "M", "U")}}


def write_calls(calls, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for c in calls:
            w.writerow(c)


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    calls, anomalies = convert(rows)
    calls_u, _ = convert(rows, u_as_pair=True)
    write_calls(calls, os.path.join(out, "calls.csv"))
    write_calls(calls_u, os.path.join(out, "upair", "calls.csv"))
    s = summarise(calls)
    s.update({"input_sha256": sha, "anomalies": anomalies})
    with open(os.path.join(out, "convert_summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1)
    print(json.dumps({k: v for k, v in s.items() if k != "fig3"}))


if __name__ == "__main__":
    main()
