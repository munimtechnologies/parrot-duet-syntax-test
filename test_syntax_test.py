# Tests for syntax_test.py (numpy only). Apache-2.0. MV2, Munim, Inc.
# Made with AI agents working in MV2's name.
import unittest

import numpy as np

import syntax_test as st


def toy_rows():
    """15 duets, 3 pairs. Each duet: F A, M a, F B, M b, F A, M a, F B, M b (A, B pair-specific)."""
    rows = []
    for d in range(15):
        p = d % 3
        A, B = "f%d" % (2 * p), "f%d" % (2 * p + 1)
        seq = [("F", A), ("M", "m" + A[1:]), ("F", B), ("M", "m" + B[1:])] * 2
        for k, (s, ty) in enumerate(seq):
            rows.append({"duet": "d%02d" % d, "pair": "p%d" % p, "pos": str(k + 1), "sex": s,
                         "type": ty})
    return rows


class TestPieces(unittest.TestCase):
    def test_mi_zero_and_one(self):
        t = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        a, b = np.array([0, 1, 2, 3]), np.array([4, 5, 6, 7])
        self.assertAlmostEqual(st.mi_bits(t, a, b, 2), 0.0, places=12)
        t2 = np.array([0, 1, 0, 1])
        self.assertAlmostEqual(st.mi_bits(t2, np.array([0, 1]), np.array([2, 3]), 2), 1.0,
                               places=12)

    def test_mi_skips_uncategorised(self):
        t = np.array([0, -1, 0, 1])
        self.assertAlmostEqual(st.mi_bits(t, np.array([0, 1]), np.array([2, 3]), 2), 0.0)

    def test_adjacent_pairs(self):
        a, b = st.adjacent_pairs(np.array([0, 0, 0, 1, 1, 2]))
        self.assertEqual(a.tolist(), [0, 1, 3])
        self.assertEqual(b.tolist(), [1, 2, 4])

    def test_window_pairs(self):
        a, b = st.window_pairs(np.array([0, 0, 0, 1]), 5)
        got = sorted(zip(a.tolist(), b.tolist()))
        self.assertEqual(got, [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])

    def test_bh(self):
        self.assertEqual(st.bh([0.01, 0.04, 0.03, 0.5]).tolist(), [True, False, False, False])
        self.assertEqual(st.bh([0.01, 0.02, 0.03, 0.04]).tolist(), [True] * 4)
        self.assertEqual(st.bh([]).tolist(), [])

    def test_permuter_keeps_groups_and_uncategorised(self):
        rng = np.random.default_rng(1)
        t = rng.integers(-1, 5, size=200)
        g = rng.integers(0, 7, size=200)
        draw = st.permuter(t, g, rng)
        changed = False
        for _ in range(5):
            x = draw()
            self.assertTrue(np.array_equal(x < 0, t < 0))
            for k in range(7):
                self.assertEqual(sorted(x[g == k].tolist()), sorted(t[g == k].tolist()))
            changed = changed or not np.array_equal(x, t)
        self.assertTrue(changed)

    def test_resampler_draws_within_group(self):
        rng = np.random.default_rng(2)
        t = rng.integers(-1, 6, size=150)
        g = rng.integers(0, 4, size=150)
        x = st.resampler(t, g, rng)()
        self.assertTrue(np.array_equal(x < 0, t < 0))
        for k in range(4):
            self.assertTrue(set(x[(g == k) & (t >= 0)].tolist())
                            <= set(t[(g == k) & (t >= 0)].tolist()))

    def test_build_corpus(self):
        rows = [{"duet": "b", "pair": "", "pos": "2", "sex": "male", "type": "x"},
                {"duet": "b", "pair": "", "pos": "1", "sex": "F", "type": ""},
                {"duet": "a", "pair": "", "pos": "1", "sex": "", "type": "y"}]
        C = st.build_corpus(rows)
        self.assertEqual(C["duet"].tolist(), [0, 1, 1])
        self.assertEqual(C["t"].tolist(), [1, -1, 0])
        self.assertEqual(C["sex"].tolist(), [2, 0, 1])
        self.assertFalse(C["has_pair"])
        self.assertEqual(C["pair"][1], C["pair"][2])
        self.assertNotEqual(C["pair"][0], C["pair"][1])


class TestAnalysis(unittest.TestCase):
    def test_planted_order_is_found(self):
        C = st.build_corpus(toy_rows())
        self.assertEqual(C["n_duets"], 15)
        self.assertEqual(C["n_pairs"], 3)
        self.assertTrue(C["has_pair"])
        res = st.analyse(C, B=99, n_worlds=5, b_cal=49, seed=7)
        self.assertIn(res["headline"], ("SYNTAX_BEYOND_REPERTOIRE", "ORDER_BEYOND_CONTENT"))
        self.assertLessEqual(res["p_B"], 0.05)
        self.assertEqual(res["n_categorised"], 120)
        self.assertIn(res["headline"], st.P8)
        self.assertEqual(set(res["grading"]["outcomes"]), set(st.PRIORS))

    def test_too_few(self):
        C = st.build_corpus(toy_rows()[:40])
        self.assertEqual(st.analyse(C, B=19, n_worlds=2, b_cal=19)["headline"], "TOO_FEW_DATA")


if __name__ == "__main__":
    unittest.main()
