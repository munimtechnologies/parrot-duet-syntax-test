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
(doi:10.5061/dryad.rn8pk0prb, CC0).

```
python -m unittest -v test_syntax_test
python syntax_test.py --data-dir data --out-dir out
```

Requires Python 3.10+ and numpy.

Made with AI agents working in MV2's name; not yet checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com. Licence: Apache-2.0 (code), CC BY 4.0 (text).
