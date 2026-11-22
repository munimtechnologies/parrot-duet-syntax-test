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

## Status (2026-11-22)

AMENDMENT-1 in SYNTAX-PREREG.md fixes the converter mapping and adds secondary checks of what
the published statistic measures. These were added after reading the paper's Table 1 and before
computing anything on the data. From the published numbers alone: every p value in Table 1 is
the two-sided Pearson p of its r with exactly **10** observations. That is not the 52 duets or
the 12 pairs. It matches Voyant's default of 10 equal segments per document, and correlations
across segments do not depend on call order. Also, 8 of the 19 positive "collocates" pair a
call type with itself, where r = 1 by definition. `test_voyant_check.py` checks this. The full
analysis job is queued; nothing about the data itself has been computed yet.

```
python -m unittest -v test_syntax_test test_convert test_voyant_check
python convert.py data/dryad_sheet01.csv data
python voyant_check.py --calls data/calls.csv --out-dir out/voyant
python syntax_test.py --data-dir data --out-dir out/syntax
```

`run_all.py` is the job script. It fetches `syntax_test.py` pinned to commit 88b350b and runs
everything. Requires Python 3.10+ and numpy.

Made with AI agents working in MV2's name; not yet checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com. Licence: Apache-2.0 (code), CC BY 4.0 (text); the data in
data/ are the authors' (Dahlin et al.), released CC0 on Dryad.
