# Tests of robust.py (AMENDMENT-2). numpy + standard library only.
# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# Made with AI agents working in MV2's name. MV2, Munim, Inc., mv2@munimtech.com
import unittest

import numpy as np

import robust as R

st = R.st


def duet_rows(name, pair, types, sexes):
    return [{"duet": name, "pair": pair, "pos": str(i + 1), "sex": s, "type": t}
            for i, (t, s) in enumerate(zip(types, sexes))]


def coupled_corpus(n_duets=40, n_pairs=4, seed=1):
    """F types random from a, b, c; each male answer fixed by the female call before it."""
    rng = np.random.default_rng(seed)
    answer = {"a": "x", "b": "y", "c": "z"}
    rows = []
    for d in range(n_duets):
        f = [str(v) for v in rng.choice(["a", "b", "c"], size=3)]
        types = [f[0], answer[f[0]], f[1], answer[f[1]], f[2], answer[f[2]]]
        rows += duet_rows("d%02d" % d, "P%d" % (d % n_pairs), types, list("FMFMFM"))
    return rows


class TestRobust(unittest.TestCase):
    def test_position_groups(self):
        rows = duet_rows("d1", "P", list("abcdef"), list("FMFMFM"))
        rows += duet_rows("d2", "P", list("gh"), list("FM"))
        C = st.build_corpus(rows)
        g = R.position_groups(C)
        # d1 (index 0): F slots 0, 2, 4 -> classes 0, 1, 2; M slots 1, 3, 5 -> 0, 1, 2
        self.assertEqual(g[:6].tolist(), [0, 3 * 1 + 0, 1, 3 * 1 + 1, 2, 3 * 1 + 2])
        # d2 (index 1): one F and one M call, both class 0
        self.assertEqual(g[6:].tolist(), [(1 * 3 + 0) * 3, (1 * 3 + 1) * 3])

    def test_dedup(self):
        rows = duet_rows("d1", "P", list("abab"), list("FMFM"))
        rows += duet_rows("d2", "Q", list("abab"), list("FMFM"))
        rows += duet_rows("d3", "P", list("abba"), list("FMFM"))
        kept, dropped = R.dedup_rows(rows)
        self.assertEqual(dropped, ["d2"])
        self.assertEqual(sorted({r["duet"] for r in kept}), ["d1", "d3"])

    def test_direction_finds_answer_coupling(self):
        C = st.build_corpus(coupled_corpus())
        out = R.direction(C, 199, np.random.default_rng(5))
        self.assertEqual(out["F_to_M"]["n_neighbour_pairs"], 120)
        self.assertEqual(out["M_to_F"]["n_neighbour_pairs"], 80)
        self.assertLessEqual(out["F_to_M"]["p"], 0.01)

    def test_position_null_fixed_when_no_middle_moves(self):
        # three calls per sex: first, middle, last are singletons, so nothing can move
        C = st.build_corpus(coupled_corpus())
        p = R.position_test(C, 49, np.random.default_rng(2))
        self.assertEqual(p["n_slots_permutable"], 0)
        self.assertEqual(p["p"], 1.0)

    def test_lopo_labels(self):
        rows = coupled_corpus(n_duets=12, n_pairs=3)
        rows += duet_rows("u1", "", list("axby"), list("FMFM"))
        out = R.lopo(rows, 19, np.random.default_rng(3))
        self.assertEqual([x["left_out"] for x in out], ["(unidentified)", "P0", "P1", "P2"])
        self.assertEqual(out[0]["n_calls_left_out"], 4)
        self.assertEqual(out[1]["n_calls_left_out"], 24)

    def test_run_smoke(self):
        res = R.run(coupled_corpus(), B=49)
        self.assertEqual(len(res["lopo"]), 4)
        self.assertGreater(len(res["dedup"]["dropped_duets"]), 0)
        rd = res["readings"]
        self.assertIn(rd["dedup"], ("ROBUST", "NOT_ROBUST"))
        self.assertTrue(rd["lopo_B"] == "ROBUST" or rd["lopo_B"].startswith("DEPENDS_ON:"))
        self.assertIn(rd["position"], ("TRANSITIONS_BEYOND_POSITION", "POSITION_MAY_EXPLAIN"))
        self.assertIn(rd["direction"], ("BOTH", "F_TO_M_ONLY", "M_TO_F_ONLY", "NEITHER"))
        self.assertEqual(sorted(res["grading"]["outcomes"]), ["R1", "R2", "R3", "R4", "R5", "R6"])

    def test_grade_brier(self):
        res = {"dedup": {"p_B": 0.001}, "lopo": [{"p_A": 0.001, "p_B": 0.5}],
               "position": {"p": 0.5}, "direction": {"F_to_M": {"p": 0.001},
                                                    "M_to_F": {"p": 0.5}}}
        g = R.grade(res)
        self.assertEqual(g["outcomes"], {"R1": True, "R2": False, "R3": True, "R4": False,
                                         "R5": True, "R6": False})
        want = (0.1 ** 2 + 0.7 ** 2 + 0.2 ** 2 + 0.5 ** 2 + 0.25 ** 2 + 0.55 ** 2) / 6
        self.assertAlmostEqual(g["brier"], want, places=12)


if __name__ == "__main__":
    unittest.main()
