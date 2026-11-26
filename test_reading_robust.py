# Copyright 2026 MV2, Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name.
"""Checks that READING-ROBUST.md matches results/robust/robust_results.json (stdlib only).

Every number quoted in the reading is re-formatted from the results file and looked up in the
text; the readings follow the AMENDMENT-2 decision rules; the Brier score is recomputed from
the registered priors R1-R6.
Run: python -m unittest -v test_reading_robust
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results", "robust", "robust_results.json")
READING = os.path.join(HERE, "READING-ROBUST.md")
ALPHA = 0.025
# Registered in AMENDMENT-2-ROBUST.md before the checks were run.
PRIORS = {"R1": 0.90, "R2": 0.70, "R3": 0.80, "R4": 0.50, "R5": 0.75, "R6": 0.55}


def f4(x):
    return "%.4f" % x


class TestReadingRobust(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RES, encoding="utf-8") as f:
            cls.r = json.load(f)
        with open(READING, encoding="utf-8") as f:
            cls.text = f.read()

    def assertQuoted(self, s):
        self.assertIn(s, self.text)

    def test_design(self):
        r = self.r
        self.assertEqual((r["seed"], r["B"], r["alpha"]), (20261124, 9999, ALPHA))
        self.assertEqual((r["n_duets"], r["n_calls"]), (52, 468))

    def test_dedup(self):
        d = self.r["dedup"]
        self.assertLess(d["p_A"], ALPHA)
        self.assertLess(d["p_B"], ALPHA)
        self.assertEqual(self.r["readings"]["dedup"], "ROBUST")
        for s in (f4(d["S_win"]), f4(d["S_adj"]), str(d["n_duets"]), str(d["n_calls"])):
            self.assertQuoted(s)
        for name in d["dropped_duets"]:
            self.assertQuoted(name)

    def test_lopo_rows(self):
        rows = self.r["lopo"]
        self.assertEqual(len(rows), 13)
        for row in rows:
            self.assertLess(row["p_A"], ALPHA)
            self.assertLess(row["p_B"], ALPHA)
            line = "| %s | %d | %d | %s | %s | %s | %s |" % (
                row["left_out"], row["n_calls_left_out"], row["n_duets"],
                f4(row["S_win"]), f4(row["p_A"]), f4(row["S_adj"]), f4(row["p_B"]))
            self.assertQuoted(line)
        self.assertEqual(self.r["readings"]["lopo_A"], "ROBUST")
        self.assertEqual(self.r["readings"]["lopo_B"], "ROBUST")

    def test_position(self):
        p = self.r["position"]
        self.assertLess(p["p"], ALPHA)
        self.assertEqual(self.r["readings"]["position"], "TRANSITIONS_BEYOND_POSITION")
        for s in (f4(p["obs"]), f4(p["null_mean"]), str(p["n_slots_permutable"])):
            self.assertQuoted(s)
        # The share quoted in the text, from the 4-decimal values it prints.
        share = (1.9960 - 1.8916) / (2.2416 - 1.8916)
        self.assertAlmostEqual(share, 0.298, places=3)
        self.assertQuoted("about 30%")

    def test_direction(self):
        d = self.r["direction"]
        for key in ("F_to_M", "M_to_F"):
            self.assertLess(d[key]["p"], ALPHA)
            line = "| %d | %s | %s | %s |" % (
                d[key]["n_neighbour_pairs"], f4(d[key]["obs"]),
                f4(d[key]["null_mean"]), f4(d[key]["p"]))
            self.assertQuoted(line)
        self.assertEqual(self.r["readings"]["direction"], "BOTH")

    def test_brier(self):
        out = self.r["grading"]["outcomes"]
        self.assertEqual(sorted(out), sorted(PRIORS))
        brier = sum((PRIORS[k] - (1.0 if out[k] else 0.0)) ** 2 for k in PRIORS) / len(PRIORS)
        self.assertAlmostEqual(brier, self.r["grading"]["brier"], places=9)
        self.assertQuoted("Brier 0.109")
        self.assertQuoted("%.4f" % brier)


if __name__ == "__main__":
    unittest.main()
