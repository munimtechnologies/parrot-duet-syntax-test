# Tests for voyant_check.py (numpy only). Apache-2.0. MV2, Munim, Inc.
# Made with AI agents working in MV2's name.
import csv
import math
import os
import tempfile
import unittest

import numpy as np

import voyant_check as vc


def write_calls(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["order", "duet", "pair", "pos", "sex", "type", "label"])
        w.writeheader()
        for r in rows:
            w.writerow(r)


def toy_rows():
    L = ["Scree", "Yoohoo", "M", "Z", "Mirror M", "Contact Call", "Unknown", "B", "Ha", "C", "O",
         "U1", "U2", "J", "K", "D", "Julia"]
    rows, o = [], 0
    for d in range(12):
        for k in range(6):
            lab = L[(d * 5 + k * 3) % len(L)]
            rows.append({"order": o, "duet": "d%02d" % d, "pair": "p%d" % (d % 3), "pos": k + 1,
                         "sex": "F" if k % 2 == 0 else "M",
                         "type": "" if lab == "Unknown" else lab, "label": lab})
            o += 1
    return rows


class TestPublishedNumbers(unittest.TestCase):
    def t_to_r(self, t, df):
        return t / math.sqrt(t * t + df)

    def test_p_from_r_matches_t_critical_values(self):
        for t, df in ((12.7062, 1), (3.182446, 3), (2.306004, 8), (2.262157, 9),
                      (2.228139, 10)):
            self.assertAlmostEqual(vc.p_from_r(self.t_to_r(t, df), df + 2), 0.05, delta=0.0005)

    def test_p_from_r_ends_and_arrays(self):
        self.assertAlmostEqual(vc.p_from_r(0.0, 10), 1.0, places=12)
        self.assertAlmostEqual(vc.p_from_r(1.0, 10), 0.0, places=12)
        self.assertAlmostEqual(vc.p_from_r(-0.5, 4), 0.5, places=12)
        p = vc.p_from_r(np.array([0.0, np.nan, 1.0]), 10)
        self.assertEqual(p.shape, (3,))
        self.assertTrue(np.isnan(p[1]))

    def test_table1_shape(self):
        self.assertEqual(len(vc.TABLE1), 23)
        self.assertEqual(sum(1 for r in vc.TABLE1 if r[0] == r[1]), 8)
        self.assertEqual(sum(1 for r in vc.TABLE1 if r[2] > 0), 19)
        self.assertEqual(sum(1 for r in vc.TABLE1 if r[2] < 0), 4)

    def test_published_p_values_fit_exactly_ten_observations(self):
        self.assertTrue(all(vc.row_consistent(r[2], r[3], 10) for r in vc.TABLE1))
        self.assertEqual(vc.fitting_n(3, 100), [10])
        self.assertFalse(all(vc.row_consistent(r[2], r[3], 52) for r in vc.TABLE1))
        self.assertFalse(all(vc.row_consistent(r[2], r[3], 12) for r in vc.TABLE1))


class TestPieces(unittest.TestCase):
    def test_tok(self):
        self.assertEqual(vc.tok("CCall"), "contactcall")
        self.assertEqual(vc.tok("Contact Call"), "contactcall")
        self.assertEqual(vc.tok("Mirror M"), "mirrorm")

    def test_bins_and_corr(self):
        t = np.array([(i // 2) % 2 for i in range(20)])
        M = vc.bin_freq(t, 2, relative=False)
        self.assertEqual(M[:, 0].tolist(), [2, 0] * 5)
        R = vc.corr(M)
        self.assertAlmostEqual(R[0, 1], -1.0, places=12)
        self.assertAlmostEqual(R[0, 0], 1.0, places=12)
        flat = vc.corr(vc.bin_freq(np.arange(20) % 2, 2, relative=True))
        self.assertTrue(np.isnan(flat[0, 1]))

    def test_context_count(self):
        t = np.array([0, 1, 0, 1])
        bl = np.array([0, 0, 1, 1])
        self.assertEqual(vc.context_count(t, bl, 0, 1, 1), 2)
        self.assertEqual(vc.context_count(t, bl, 0, 1, 1, both=True), 3)
        self.assertEqual(vc.context_count(t, bl, 0, 1, 1, both=True, within=True), 2)
        self.assertEqual(vc.context_count(t, bl, 0, 1, 3), 3)

    def test_shuffles(self):
        rng = np.random.default_rng(3)
        t = np.arange(12)
        bl = np.repeat([0, 1, 2], 4)
        x = vc.within_shuffle(t, bl, rng)
        for b in range(3):
            self.assertEqual(sorted(x[4 * b:4 * b + 4].tolist()), list(range(4 * b, 4 * b + 4)))
        y = vc.placement_shuffle(t, bl, rng)
        chunks = sorted(y[4 * b:4 * b + 4].tolist() for b in range(3))
        self.assertEqual(chunks, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])

    def test_load_stream(self):
        rows = [{"order": 2, "duet": "b", "pair": "", "pos": 1, "sex": "F", "type": "",
                 "label": "Unknown"},
                {"order": 0, "duet": "a", "pair": "", "pos": 1, "sex": "F", "type": "Z",
                 "label": "Z"},
                {"order": 1, "duet": "a", "pair": "", "pos": 2, "sex": "M", "type": "Mirror M",
                 "label": "Mirror M"}]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "calls.csv")
            write_calls(p, rows)
            t, bl, vocab = vc.load_stream(p, True)
            t2, bl2, vocab2 = vc.load_stream(p, False)
        self.assertEqual([vocab[i] for i in t], ["z", "mirrorm", "unknown"])
        self.assertEqual(bl.tolist(), [0, 0, 1])
        self.assertEqual([vocab2[i] for i in t2], ["z", "mirrorm"])


class TestAnalysis(unittest.TestCase):
    def test_smoke(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "calls.csv")
            write_calls(p, toy_rows())
            res = vc.analyse(p, n_shuffle=5)
            vc.write_results(res, os.path.join(d, "out"))
            self.assertTrue(os.path.exists(os.path.join(d, "out", "RESULTS-VOYANT.md")))
            self.assertTrue(os.path.exists(os.path.join(d, "out", "voyant_results.json")))
        self.assertEqual(res["n_fitting_published_p"], [10])
        self.assertIn(res["R1_reading"], ("REPRODUCED", "PARTLY_REPRODUCED", "NOT_REPRODUCED"))
        self.assertIn(res["R2a_reading"], ("NOT_APPLICABLE", "ORDER_BLIND", "ORDER_SENSITIVE"))
        self.assertIn(res["R2b_reading"], ("CHANCE_LEVEL", "EXCESS_AT_BIN_SCALE"))
        self.assertEqual(len(res["R1_variants"]), 4)
        self.assertEqual(len(res["R1_context"]), 8)
        n_unk = sum(1 for r in toy_rows() if r["label"] == "Unknown")
        self.assertGreater(n_unk, 0)
        self.assertIn(res["R2"]["n_tokens"], (72, 72 - n_unk))


if __name__ == "__main__":
    unittest.main()
