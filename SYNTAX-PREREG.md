# parrot-duet-syntax-test: pre-registration

Registered 2026-11-22 (UTC), before any MV2 agent has opened the data. Made with AI agents
working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code Apache-2.0, text CC BY 4.0.

## The claim

Dahlin, Killinger, Snipe, Small, Guenther and Richwine (2026), "Decoding parrot duets: complex
communication in yellow-naped amazons", Journal of Avian Biology 2026: e03552,
doi:10.1002/jav.03552 (CC BY 3.0). Warble duets of wild yellow-naped amazon pairs (Costa Rica;
about 54 duets from 13 mated pairs, more than 450 calls) use 36 call types; calls "assort
non-randomly" and follow more than 20 "syntactic rules", found as collocates with the humanities
text tool Voyant. 58% of call types are sex-biased or sex-specific. The press covered it as
"syntax discovered in wild parrots" (EurekAlert, phys.org, Popular Science, Discover, Forbes).

## Why a re-test is needed

1. Voyant counts how often words occur near each other (default context: 5 words each side). It
   has no null model. A warble duet is 5-10 s long and has about 9 calls, so a 5-call window covers
   most of a duet: a "collocate" is then close to "sung in the same duet".
2. Co-occurrence in a duet is produced by **who sings**: each pair has its own repertoire
   (Dahlin and Wright 2009 found most duet variation at the within-pair level), and male and female
   calls are mostly different types. Pooling 13 pairs' duets creates collocates (and "negative
   collocates") without any rule about order.
3. The calls were assigned to sexes by the group's earlier rule that female and male calls
   alternate, female first. Any "female X then male Y" pattern partly restates that labelling rule.

Question: do the duets show (A) co-occurrence beyond each pair's and each sex's repertoire, and
(B) order beyond what each duet contains? Only (B) is syntax in the linguistic sense.

## Data

Dryad doi:10.5061/dryad.rn8pk0prb, version 421527, licence CC0-1.0:
`Supplement_Data_DRYAD.xlsx` 65,456 bytes, sha256
bf21a76da9f06a8c1ba02c0bcef608f2301e82b07c20c5f8ad445de86679db8b; `README.md` 2,462 bytes, sha256
3021e68da05d6fbdaebd928bcb4c82fb095c594aa68d861d68873accc6c2a209. Dryad refuses automated
downloads, so a person-operated browser saves the two files; their sha256 must match the values
above or the study stops. Because the data are CC0 they may be committed to this repository.

A converter (`convert.py`, written after this registration and after reading the file layout)
turns the spreadsheet into `data/calls.csv` with one row per call: `duet, pair, pos, sex, type`.
Converter rules fixed now: (i) one duet = one recorded warble-duet sequence as the authors
delimit it; (ii) `pos` = the authors' call order; (iii) `sex` = the authors' assignment (F/M),
blank if none; (iv) `type` = the authors' call-type label; labels the authors mark as
uncategorised, rare or unknown become blank (they keep their slot, so no false adjacency is
created by deleting them); (v) `pair` = the authors' pair or territory identifier, blank if the
file has none. The converter may not drop, merge or relabel any call type. If the file gives no
duet boundaries or no call order, the headline is SCHEMA_UNRESOLVED and nothing else is computed.
Any converter decision not covered here goes in a dated AMENDMENT section below, written before
`syntax_test.py` is run on the real data.

## Statistics (all in `syntax_test.py`)

Slots keep their duet, position, sex and pair. Only the call-type labels of categorised slots are
permuted, and only inside groups:

- N0 pooled: across the whole corpus (the naive "non-random" null; ignores sex and pair).
- N1 sex: within sex across the corpus.
- N2 pair x sex: within each pair's own calls of one sex, across that pair's duets.
- N3 duet x sex: within each duet and sex (keeps exactly what each duet contains; tests order).

Statistics, both plug-in mutual information in bits between the type labels of slot pairs:

- S_adj: ordered adjacent pairs inside a duet (position i, i+1).
- S_win: all pairs inside a duet at distance 1 to 5, both directions (Voyant's default context).

Pairs with an uncategorised slot are skipped. p = (1 + #{null >= observed}) / (B + 1), B = 9,999,
seed 20261122.

**Primary A (co-occurrence beyond repertoire):** S_win under N2. If the data have no pair
identifier, A is run under N1 and flagged A_WEAK.
**Primary B (order beyond duet content = syntax):** S_adj under N3.
Each primary is judged at alpha = 0.025 (Bonferroni over two).

Secondary (reported, not part of the headline):
- S1: S_adj and S_win under N0 and N1 (the naive tests).
- S2 rule counts: every ordered adjacent type pair (x, y) observed at least 3 times; two-sided
  permutation p of its count around the null mean, under N0, N2 and N3; Benjamini-Hochberg at
  q = 0.05 within each null; count of positive and negative "rules" surviving per null.
- S3 self-repeats: share of adjacent pairs with the same type, two-sided under N3.
- S4 whole-duet repeats: duets whose full type sequence equals another duet's (descriptive).
- R0 reproduction: counts of duets, pairs, calls, categorised call types, compared with the
  paper's 54 / 13 / >450 / 36.

## Calibration (on the real slot structure)

- W0 (no syntax): each categorised slot's type is redrawn with replacement from its own
  pair x sex labels (sex labels only if no pair identifier). 200 worlds, B = 499 per test.
  Reported: false-alarm rate at 0.05 of S_adj and S_win under N0 (the naive tests), and size of
  both primaries at 0.025.
- W1 (planted order rule): a W0 world in which, after each slot of type x, the next slot is set to
  type y with probability 0.3 when it has y's majority sex, where (x, y) is the most frequent
  observed adjacent pair with x != y. 200 worlds, B = 499. Reported: power of primary B.

## Headline (first rule that applies)

1. SCHEMA_UNRESOLVED: no duet boundaries or no call order, or sha256 mismatch.
2. TOO_FEW_DATA: fewer than 10 duets or fewer than 100 categorised calls.
3. SYNTAX_BEYOND_REPERTOIRE: p_A < 0.025 and p_B < 0.025.
4. ORDER_BEYOND_CONTENT: p_B < 0.025 only.
5. COOCCURRENCE_ONLY: p_A < 0.025 only.
6. EXPLAINED_BY_REPERTOIRE: neither, and power of B in W1 >= 0.8.
7. UNDERPOWERED: neither, and power of B in W1 < 0.8.

## Priors (graded with Brier scores in the results)

- P1 S_adj under N0 has p < 0.05: 0.85
- P2 false-alarm rate of S_win under N0 in W0 is >= 0.50: 0.65
- P3 p_B < 0.025: 0.55
- P4 p_A < 0.025: 0.35
- P5 both primaries have size <= 0.05 in W0: 0.85
- P6 power of B in W1 >= 0.8: 0.55
- P7 fewer than 20 adjacent rules survive BH under N3: 0.90
- P8 headline: SYNTAX_BEYOND_REPERTOIRE 0.20, ORDER_BEYOND_CONTENT 0.35, COOCCURRENCE_ONLY 0.10,
  EXPLAINED_BY_REPERTOIRE 0.20, UNDERPOWERED 0.15.

## What would be remarkable

If B holds: the first calibrated evidence that a wild parrot orders calls in a duet beyond what the
duet contains, which is a far stronger result than the published collocate counts. If A and B both
fail with power: a widely covered "syntax" result is explained by who sings, and the field gets a
reusable check for text-tool analyses of animal sequences.

## Limits fixed in advance

The labels and the sex assignment are the authors'. Order within a sex is tested; the
female-male alternation itself is not, because the labelling rule built it in. About 54 duets is a
small corpus; the calibration says how much it can detect. No acoustics are re-analysed.

## Amendments

(none yet)
