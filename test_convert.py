# Tests for convert.py (standard library only). Apache-2.0. MV2, Munim, Inc.
# Made with AI agents working in MV2's name.
import csv
import os
import tempfile
import unittest

import convert as cv


def sheet(rows):
    return [{"Duet Name": d, "Pair": p, "Note #": n, "Call Type": t, "Sex (M,F,U)": s,
             "Total Note Duration (s) ": "0.1"} for d, p, n, t, s in rows]


class TestConvert(unittest.TestCase):
    def test_mapping(self):
        rows = sheet([("A_1  ", "RW", "1", "Z ", "F"), ("A_1", "RW", "2", "Unknown", "M"),
                      ("A_1", "RW", "3", "Mirror  M", "u"), ("B_2", "U", "1", "U1", "F")])
        calls, an = cv.convert(rows)
        self.assertEqual(an, [])
        self.assertEqual([c["duet"] for c in calls], ["A_1", "A_1", "A_1", "B_2"])
        self.assertEqual([c["type"] for c in calls], ["Z", "", "Mirror M", "U1"])
        self.assertEqual(calls[1]["label"], "Unknown")
        self.assertEqual([c["sex"] for c in calls], ["F", "M", "U", "F"])
        self.assertEqual([c["pos"] for c in calls], [1, 2, 3, 1])
        self.assertEqual([c["order"] for c in calls], [0, 1, 2, 3])
        self.assertEqual(calls[0]["pair"], "RW")
        self.assertEqual(calls[3]["pair"], "")
        calls_u, _ = cv.convert(rows, u_as_pair=True)
        self.assertEqual(calls_u[3]["pair"], "U")

    def test_anomalies(self):
        rows = sheet([("A", "RW", "1", "Z", "F"), ("B", "RW", "1", "Z", "F"),
                      ("A", "RW", "2", "Z", "M"), ("B", "RW", "3", "Z", "F")])
        _, an = cv.convert(rows)
        self.assertEqual(len(an), 4)
        self.assertEqual(sum("not contiguous" in a for a in an), 2)

    def test_missing_column(self):
        with self.assertRaises(KeyError):
            cv.convert([{"x": "1"}])

    def test_summary(self):
        rows = sheet([("A", "RW", "1", "Scree", "F"), ("A", "RW", "2", "Scree", "U"),
                      ("A", "RW", "3", "Unknown", "M"), ("B", "CD8", "1", "Foo", "M")])
        s = cv.summarise(cv.convert(rows)[0])
        self.assertEqual(s["n_duets"], 2)
        self.assertEqual(s["n_calls"], 4)
        self.assertEqual(s["n_unknown"], 1)
        self.assertEqual(s["n_types"], 2)
        self.assertEqual(s["pairs"], ["CD8", "RW"])
        self.assertEqual(s["labels_not_in_fig3"], ["foo"])
        self.assertEqual(s["fig3"]["scree"], {"paper": 41, "all": 2, "sexed": 1})
        self.assertEqual(s["sex_counts"], {"F": 1, "M": 2, "U": 1})

    def test_write_roundtrip(self):
        calls, _ = cv.convert(sheet([("A", "RW", "1", "Scree", "F")]))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "calls.csv")
            cv.write_calls(calls, p)
            with open(p, newline="", encoding="utf-8") as f:
                back = list(csv.DictReader(f))
        self.assertEqual(back, [{"order": "0", "duet": "A", "pair": "RW", "pos": "1",
                                 "sex": "F", "type": "Scree", "label": "Scree"}])


if __name__ == "__main__":
    unittest.main()
