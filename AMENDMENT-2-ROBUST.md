# AMENDMENT-2: robustness checks (2026-11-24 UTC)

Written **after** the registered primaries were graded (READING-SYNTAX.md), and before any of the
checks below was run. They are secondary. They cannot change the registered headline
(SYNTAX_BEYOND_REPERTOIRE). Their job is to show whether that headline rests on one pair, on
repeated duets, or only on where calls sit in a duet. Made with AI agents working in MV2's name
(MV2, Munim, Inc., mv2@munimtech.com).

Code: `robust.py` (tests in `test_robust.py`). The job is `run_robust.py`, which fetches
`syntax_test.py`, `convert.py` and `data/dryad_sheet01.csv` from commit
7f0d2595e8fe38700856c1f1dbb657d81aca2f0e and stops unless the engine and the sheet match the
sha256 values recorded in results/run_manifest.json. Seed 20261124, B = 9,999 for every test,
alpha 0.025 (the primaries' level).

- **D, duplicates.** Drop every duet whose full call-type sequence equals an earlier duet's
  (the engine reported 4 duets that repeat another). Rerun primaries A and B.
  ROBUST if both p < 0.025.
- **L, leave one pair out.** Remove one pair at a time (12 pairs), and the unidentified duets as
  one more unit. Rerun A and B each time. ROBUST if every p < 0.025. Otherwise
  DEPENDS_ON:<the pairs whose removal pushes p to 0.025 or above>.
- **P, position-only null.** Call types are permuted only among calls of the same duet, sex
  and position class. The classes are the first, middle and last call of that sex in the duet.
  So openers and closers stay fixed, and only the order of the middle calls is tested.
  Statistic: S_adj. TRANSITIONS_BEYOND_POSITION if p < 0.025, else POSITION_MAY_EXPLAIN.
  (This null is conservative: in duets with three or fewer calls per sex nothing can move.)
- **F, direction.** S_adj is computed only on female-then-male neighbours, then only on
  male-then-female neighbours, each under null N3 (within duet and sex). The reading is BOTH,
  F_TO_M_ONLY, M_TO_F_ONLY or NEITHER at p < 0.025. Female-then-male is the answer within a
  note pair. Male-then-female is the step to the next pair.

Priors (Brier-graded): R1 D keeps B significant 0.90; R2 every leave-one-out B < 0.025 0.70;
R3 every leave-one-out A < 0.025 0.80; R4 TRANSITIONS_BEYOND_POSITION 0.50; R5 female-then-male
p < 0.025 0.75; R6 male-then-female p < 0.025 0.55.
