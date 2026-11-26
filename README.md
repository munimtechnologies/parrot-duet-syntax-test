# parrot-duet-syntax-test

An open, pre-registered re-test of the 2026 report that wild yellow-naped amazon parrots follow
"more than 20 syntactic rules" in their warble duets (Dahlin et al. 2026, Journal of Avian Biology
e03552, doi:10.1002/jav.03552). The rules were found as collocates with Voyant, a text-analysis
tool with no null model.

A duet is short (about 9 calls), each pair has its own repertoire, and male and female calls are
mostly different types, so calls can "go together" just because the same birds sang them. This
study asks two things, each against calibrated permutation nulls:

- **A, co-occurrence:** do call types occur near each other more than each pair's own
  repertoire (by sex) predicts?
- **B, order (syntax):** given exactly which calls a duet contains, is their order structured?

The plan, tests, decision rules and priors are in [SYNTAX-PREREG.md](SYNTAX-PREREG.md), fixed
before any of our agents opened the data. The authors' data are public on Dryad
(doi:10.5061/dryad.rn8pk0prb, CC0); a copy of the sheet is in [data/](data/).

## Result (graded 2026-11-24): read [READING-SYNTAX.md](READING-SYNTAX.md)

- **The order is real.** Both registered primaries are significant: A p 0.0001 (test size
  0.045) and B p 0.0001 (test size 0.030). Headline SYNTAX_BEYOND_REPERTOIRE. Nine ordered call
  pairs survive a within-duet null, for example Mirror F followed by Mirror M (6 times against
  1.43 expected).
- **The published statistic does not measure order.** Every Table 1 p value fits only n = 10
  observations. Pearson correlations of call-type counts across 10 equal slices of the data file
  (Voyant's default) reproduce 14 of the 15 between-type rows to three decimals. Shuffling calls
  inside duets barely changes them. Placing whole duets in random order removes most of them:
  16.7% of the Table 1 pairs stay significant.

## Robustness (AMENDMENT-2, graded 2026-11-26): read [READING-ROBUST.md](READING-ROBUST.md)

Registered in [AMENDMENT-2-ROBUST.md](AMENDMENT-2-ROBUST.md) before these checks were run. All
four came out ROBUST, and all six registered predictions came true (Brier 0.109):

- **Repeated duets removed** (2 duets): A and B both p 0.0001.
- **Leave one pair out** (12 pairs and the unidentified birds, one at a time): every A and B
  p is 0.0001, including without RW, the pair that sang 152 of the 468 calls.
- **Position-only null** (openers and closers kept in place): 2.2416 bits against 1.9960,
  p 0.0001. Fixed positions explain about 30% of the order effect; the rest is order among the
  middle calls.
- **Direction:** female-then-male (2.6387 against 2.1943) and male-then-female (2.5450 against
  2.2956) neighbours are both structured, p 0.0001 each.

```
python -m unittest -v test_syntax_test test_convert test_voyant_check test_robust test_reading_robust
python convert.py data/dryad_sheet01.csv data
python voyant_check.py --calls data/calls.csv --out-dir out/voyant
python syntax_test.py --data-dir data --out-dir out/syntax
python robust.py --calls data/calls.csv --out-dir out/robust
```

`run_all.py` is the graded job. It fetches `syntax_test.py` pinned to commit 88b350b and runs
everything. `run_robust.py` is the AMENDMENT-2 job (its outputs are in
[results/robust/](results/robust/)). Requires Python 3.10+ and numpy.

Made with AI agents working in MV2's name; not yet checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com. Licence: Apache-2.0 (code), CC BY 4.0 (text); the data in
data/ are the authors' (Dahlin et al.), released CC0 on Dryad.
