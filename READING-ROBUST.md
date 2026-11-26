# Reading: AMENDMENT-2 robustness checks (graded 2026-11-26)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; not yet checked
by a human expert. Text CC BY 4.0. Every number below is copied from
[results/robust/robust_results.json](results/robust/robust_results.json) and
[results/robust/RESULTS-ROBUST.md](results/robust/RESULTS-ROBUST.md). They were produced by the
job `parrot-robust-v1` (2026-11-26, Python 3.12, numpy 2.1.3) under
[AMENDMENT-2-ROBUST.md](AMENDMENT-2-ROBUST.md), which was written after the primaries were graded
and before any of these checks was run. The job fetched `syntax_test.py`, `convert.py` and the
data sheet from commit 7f0d2595e8fe38700856c1f1dbb657d81aca2f0e. Their sha256 values matched the
registered ones, with no mismatch ([results/robust/robust_manifest.json](results/robust/robust_manifest.json)).
Seed 20261124, B = 9,999 permutations per test, alpha 0.025.

## In one paragraph

The order found in the yellow-naped amazon warble duets ([READING-SYNTAX.md](READING-SYNTAX.md))
does not rest on one pair, on repeated duets, or only on fixed opening and closing calls. Every
registered check came out the way the stronger reading needs. Both primaries stayed at p 0.0001
when the duplicated duets were removed, and when each of the 12 pairs (and the unidentified birds)
was left out in turn. The order statistic beat a null that keeps every call's position class
(first, middle, last of its sex in the duet): p 0.0001. The dependence runs both ways, from a
female call to the male answer and from a male call to the next female call. All six registered
predictions came true (Brier 0.109). These are secondary checks and cannot change the registered
headline, SYNTAX_BEYOND_REPERTOIRE.

## D: repeated duets removed

Dropping every duet whose full call sequence repeats an earlier one removed 2 duets
(CD23_AH25JAN08PW2 and RW_AH1FEB07AW2), leaving 50 duets and 449 calls. Co-occurrence (A):
1.0582 bits, p 0.0001. Order (B): 2.1703 bits, p 0.0001. Reading **ROBUST**.

## L: leave one pair out

| left out | calls removed | duets left | A (bits) | A p | B (bits) | B p |
|---|---|---|---|---|---|---|
| (unidentified) | 34 | 48 | 1.1099 | 0.0001 | 2.2513 | 0.0001 |
| A1 | 6 | 51 | 1.0976 | 0.0001 | 2.2483 | 0.0001 |
| AG | 39 | 48 | 1.1032 | 0.0001 | 2.2743 | 0.0001 |
| BC | 15 | 50 | 1.1109 | 0.0001 | 2.2892 | 0.0001 |
| CD10 | 3 | 51 | 1.0962 | 0.0001 | 2.2535 | 0.0001 |
| CD17 | 26 | 49 | 1.1347 | 0.0001 | 2.2908 | 0.0001 |
| CD23 | 26 | 49 | 1.0254 | 0.0001 | 2.1477 | 0.0001 |
| CD8 | 19 | 49 | 1.1025 | 0.0001 | 2.2944 | 0.0001 |
| FW | 91 | 41 | 1.1685 | 0.0001 | 2.4239 | 0.0001 |
| LP | 18 | 49 | 1.1069 | 0.0001 | 2.2847 | 0.0001 |
| RC | 21 | 50 | 1.1088 | 0.0001 | 2.2734 | 0.0001 |
| RW | 152 | 39 | 1.3310 | 0.0001 | 2.5892 | 0.0001 |
| UB | 18 | 50 | 1.0528 | 0.0001 | 2.1937 | 0.0001 |

Every p is below 0.025 for both tests, so both readings are **ROBUST**. The pair RW sang 152 of
the 468 calls (about a third). Without RW both tests still give p 0.0001, so the result does not
come from the best-recorded pair. The bits are not comparable across rows: plug-in information
estimates rise as the sample shrinks, which is why each row has its own permutation null.

## P: position-only null

Call types were shuffled only among calls of the same duet, sex and position class, so openers
and closers stay in place and only the order of the middle calls can change (227 calls could
move). Observed 2.2416 bits against a null mean of 1.9960, p 0.0001: **TRANSITIONS_BEYOND_POSITION**.
Fixed positions explain part of the order effect, but not all of it. Using the within-duet null
mean of the primary test (1.8916, READING-SYNTAX.md), position accounts for
(1.9960 - 1.8916) / (2.2416 - 1.8916) = 0.1044 / 0.3500, about 30% of the excess over that null.
The rest is order among the middle calls.

## F: direction

| neighbours | pairs | observed (bits) | null mean | p |
|---|---|---|---|---|
| female call, then male call (answer within a note pair) | 204 | 2.6387 | 2.1943 | 0.0001 |
| male call, then female call (step to the next note pair) | 179 | 2.5450 | 2.2956 | 0.0001 |

Reading **BOTH**: which female call comes next depends on the male call before it, as well as
which male call answers which female call.

## Priors (Brier)

R1 (0.90), R2 (0.70), R3 (0.80), R4 (0.50), R5 (0.75), R6 (0.55): all six came true.
Brier score 0.109 (0.1092). Our least confident call was R4: we gave the position-only
null an even chance of explaining the order effect away, and it did not.

## Limits

- p 0.0001 is the smallest value 9,999 permutations can give, so these runs show that every
  check passed, not how far past the threshold each one is.
- Only the primary B test was size-calibrated (false-alarm rate 0.030 in 200 no-syntax worlds).
  The leave-one-out and duplicate runs reuse that statistic on subsets. The position-only and
  direction nulls were not separately calibrated. The position null is conservative: in duets
  with three or fewer calls of one sex nothing can move.
- The sex of each call is the authors', assigned by the rule that female and male calls
  alternate, female first. The direction result is about which call types follow which, not
  about the alternation itself, which is not tested.
- 52 duets from 12 pairs is a small sample. The nine named ordered call pairs in
  READING-SYNTAX.md still rest on 3 to 8 occurrences each, and these checks do not test them one
  by one.
- A defined order of sex-specific notes in this species' duets was described by
  [Wright and Dahlin (2007)](https://doi.org/10.1163/156853907779947346). What these checks add
  is evidence that the order in the 2026 warble duets survives the obvious confounds.

Paper: Dahlin, Killinger, Snipe, Small, Guenther and Richwine 2026, Journal of Avian Biology
e03552, [doi:10.1002/jav.03552](https://doi.org/10.1002/jav.03552). Data: Dryad
doi:10.5061/dryad.rn8pk0prb (CC0).
