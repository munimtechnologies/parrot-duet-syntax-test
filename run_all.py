# run_all.py: the parrot-syntax job (SYNTAX-PREREG.md with AMENDMENT-1). Standard library only.
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Fetches the registered engine (syntax_test.py pinned to commit 88b350b) and the authors' data
from the public repository, converts the data, then runs the Voyant check and both primaries.

python run_all.py --out-dir /out
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/parrot-duet-syntax-test"
PIN = "88b350b7e2dfeeee09d89a4b93127e00bad5f9c8"
XLSX_SHA = "bf21a76da9f06a8c1ba02c0bcef608f2301e82b07c20c5f8ad445de86679db8b"
HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(url, dest, tries=4):
    err = ""
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            return hashlib.sha256(data).hexdigest()
        except Exception as e:  # network hiccup: retry
            err = repr(e)
            time.sleep(20 * (k + 1))
    raise RuntimeError("download failed: %s: %s" % (url, err))


def norm(s):
    return " ".join(str("" if s is None else s).split())


def xlsx_check(xlsx, sheet_csv):
    """Optional: re-read the sha-checked xlsx and compare the five used columns with the CSV."""
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-q",
                    "openpyxl==3.1.5"], check=False)
    try:
        import openpyxl
    except ImportError:
        return None
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    xr = [[norm(v) for v in row] for row in wb.worksheets[0].iter_rows(values_only=True)]
    wb.close()
    with open(sheet_csv, newline="", encoding="utf-8-sig") as f:
        cr = [[norm(v) for v in row] for row in csv.reader(f)]
    if len(xr) != len(cr):
        return False
    return all(a[:5] == b[:5] for a, b in zip(xr, cr))


def step(cmd, log):
    p = subprocess.run(cmd, capture_output=True, text=True)
    log.append({"cmd": cmd[1:], "rc": p.returncode, "stdout": p.stdout[-4000:],
                "stderr": p.stderr[-4000:]})
    print(" ".join(cmd[1:]), "->", p.returncode, flush=True)
    print(p.stdout[-2000:], p.stderr[-2000:], flush=True)
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args()
    out = args.out_dir
    src = os.path.join(out, "src")
    os.makedirs(src, exist_ok=True)
    man = {"pinned_engine_commit": PIN, "steps": []}
    man["syntax_test_sha256"] = fetch(RAW + "/" + PIN + "/syntax_test.py",
                                      os.path.join(src, "syntax_test.py"))
    sheet = os.path.join(src, "dryad_sheet01.csv")
    man["sheet_csv_sha256"] = fetch(RAW + "/main/data/dryad_sheet01.csv", sheet)
    try:
        xl = os.path.join(src, "Supplement_Data_DRYAD.xlsx")
        man["xlsx_sha256"] = fetch(RAW + "/main/data/Supplement_Data_DRYAD.xlsx", xl, tries=2)
        man["xlsx_sha256_matches_registration"] = man["xlsx_sha256"] == XLSX_SHA
        man["xlsx_matches_csv"] = xlsx_check(xl, sheet)
    except Exception as e:
        man["xlsx_check_error"] = repr(e)
    py = sys.executable
    rcs = [step([py, os.path.join(HERE, "convert.py"), sheet, os.path.join(out, "data")],
                man["steps"])]
    rcs.append(step([py, os.path.join(HERE, "voyant_check.py"), "--calls",
                     os.path.join(out, "data", "calls.csv"), "--out-dir",
                     os.path.join(out, "voyant")], man["steps"]))
    rcs.append(step([py, os.path.join(src, "syntax_test.py"), "--data-dir",
                     os.path.join(out, "data"), "--out-dir", os.path.join(out, "syntax")],
                    man["steps"]))
    rcs.append(step([py, os.path.join(src, "syntax_test.py"), "--data-dir",
                     os.path.join(out, "data", "upair"), "--out-dir",
                     os.path.join(out, "syntax_upair")], man["steps"]))
    with open(os.path.join(out, "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    sys.exit(0 if all(rc == 0 for rc in rcs) else 1)


if __name__ == "__main__":
    main()
