# run_robust.py: the AMENDMENT-2 job of parrot-duet-syntax-test. Standard library only.
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
"""Fetches the registered engine, the converter and the authors' sheet from the public repository
at a fixed commit, checks the engine and sheet hashes, converts, then runs robust.py.

python run_robust.py --out-dir /out --fetch-only   (fetch, check, convert)
python run_robust.py --out-dir /out                (fetch, check, convert, run)
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

RAW = "https://raw.githubusercontent.com/munimtechnologies/parrot-duet-syntax-test"
PIN = "7f0d2595e8fe38700856c1f1dbb657d81aca2f0e"
SHA = {"syntax_test.py": "ceea7e0604f781e844574cc4386933a032d690e4c84920b83dbc845a21a01cf7",
       "data/dryad_sheet01.csv":
           "e86807d2c7cfd48bf7a4610274e545d62c726e92797c4956d4fee2141d0e03be"}
HERE = os.path.dirname(os.path.abspath(__file__))


def fetch(path, dest, tries=4):
    err = ""
    for k in range(tries):
        try:
            with urllib.request.urlopen(RAW + "/" + PIN + "/" + path, timeout=60) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            return hashlib.sha256(data).hexdigest()
        except Exception as e:  # network hiccup: retry
            err = repr(e)
            time.sleep(20 * (k + 1))
    raise RuntimeError("download failed: %s: %s" % (path, err))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--fetch-only", action="store_true")
    args = ap.parse_args()
    out = args.out_dir
    src = os.path.join(out, "src")
    os.makedirs(src, exist_ok=True)
    man = {"pin": PIN, "sha256": {}}
    for path in ("syntax_test.py", "convert.py", "data/dryad_sheet01.csv"):
        man["sha256"][path] = fetch(path, os.path.join(src, os.path.basename(path)))
    bad = [p for p, h in SHA.items() if man["sha256"][p] != h]
    man["hash_mismatch"] = bad
    with open(os.path.join(out, "robust_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    if bad:
        print("STOP: hash mismatch", bad, flush=True)
        sys.exit(2)
    data = os.path.join(out, "data")
    p = subprocess.run([sys.executable, os.path.join(src, "convert.py"),
                        os.path.join(src, "dryad_sheet01.csv"), data],
                       capture_output=True, text=True)
    print(p.stdout[-2000:], p.stderr[-2000:], flush=True)
    if p.returncode != 0:
        sys.exit(p.returncode)
    if args.fetch_only:
        return
    env = dict(os.environ, SYNTAX_SRC=src)
    p = subprocess.run([sys.executable, os.path.join(HERE, "robust.py"), "--calls",
                        os.path.join(data, "calls.csv"), "--out-dir",
                        os.path.join(out, "robust")], capture_output=True, text=True, env=env)
    print(p.stdout[-4000:], p.stderr[-4000:], flush=True)
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
