# Reading: parrot-duet-syntax-test (graded 2026-11-24)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; not yet checked
by a human expert. Text CC BY 4.0. Every number below is copied from the files in
[results/](results/), produced by the job `parrot-syntax-v1` (2026-11-24, 977 s) under
[SYNTAX-PREREG.md](SYNTAX-PREREG.md) with AMENDMENT-1. The data are the authors' CC0 sheet
(sha256 matched the registration).

## In one paragraph

Wild yellow-naped amazon pairs really do order the calls of their warble duets. Under the
registered, calibrated tests, the order of calls inside a duet carries more information than the
duet's own calls in random order (p 0.0001; the test's false-alarm rate in no-order worlds was
0.030). Calls also co-occur beyond what each pair's own repertoire predicts (p 0.0001; size
0.045). So the headline claim of Dahlin et al. (2026) survives. **The published evidence for it
does not measure order, however.** Every p value in the paper's Table 1 fits only n = 10
observations. We reproduced the between-type correlations of Table 1 to three decimals for 14
of its 15 rows as Pearson correlations of call-type counts across ten equal slices of the data
file, which is Voyant's default. Those correlations hardly change when the calls inside every
duet are shuffled. They mostly vanish when whole duets are put in a random order in the file.

## Data as converted

52 duets, 12 identified pairs plus duets of unidentified birds, 468 calls (457 with a call type),
36 call types (results/convert_summary.json). This matches the paper's "52 duets from 12 pairs"
used for its syntax analysis.

## Registered primaries

| test | observed (bits) | null mean | p |
|---|---|---|---|
| A: co-occurrence within 5 calls, null within pair and sex | 1.0904 | 0.5317 | 0.0001 |
| B: adjacent order, null within duet and sex | 2.2416 | 1.8916 | 0.0001 |

p 0.0001 is the smallest value 9,999 permutations can give. Headline (registered rule 3):
**SYNTAX_BEYOND_REPERTOIRE**. The sensitivity run that treats the unidentified duets as one pair
gives the same headline, with A p 0.0001 and B p 0.0001 (results/syntax_upair/).

**Calibration** (200 no-syntax worlds, in which each call's type is redrawn from its own pair's
and sex's calls): the naive pooled tests ("calls assort non-randomly") fired in every world
(false-alarm rate 1.000 for both statistics). The registered primaries fired at 0.045 (A) and
0.030 (B). Power of B to detect one planted weak rule (Scree followed by Yoohoo with probability
0.3) was only 0.105. So a non-significant B would have meant little. The observed order effect
is far larger than that planted rule.

## Which transitions carry the order

Of 44 ordered neighbour pairs seen at least 3 times, Benjamini-Hochberg at q 0.05 keeps 31 under
the pooled null, 26 under the pair-and-sex null and **9 under the within-duet null**. None of the
9 is a negative ("avoided") pair.

| first call | next call | seen | expected (within-duet null) | p |
|---|---|---|---|---|
| Mirror F | Mirror M | 6 | 1.43 | 0.0006 |
| Hoo | Ha | 5 | 1.02 | 0.0007 |
| J Fancy | O | 5 | 1.15 | 0.0008 |
| K | Z | 3 | 0.43 | 0.0013 |
| U1 | U2 | 7 | 3.18 | 0.0038 |
| Scree | Scree | 8 | 3.80 | 0.0047 |
| O | Alien | 3 | 0.56 | 0.0056 |
| Nert | Mirror F | 3 | 0.56 | 0.0078 |
| Flert | Nert | 3 | 0.61 | 0.0091 |

Self-repeats overall are not above chance (0.0852 of neighbour pairs against 0.0733, p 0.2007).
Four duets repeat another duet's full sequence exactly. AMENDMENT-2 checks that they do not
carry the result.

## What the published statistic measures (AMENDMENT-1, secondary)

- **T.** Of all n from 3 to 100, only n = 10 makes every one of the 23 published p values match
  its r. Eight of the 23 rows pair a call type with itself, where r = 1 by definition.
- **R1, REPRODUCED.** We cut the calls, in file order, into 10 equal slices and counted each type
  in each slice. Pearson r between two types' counts reproduces Table 1: the median absolute
  difference over the 15 between-type rows is 0.0002, and 14 of the 15 rows agree to three
  decimals. The row C with O does not reproduce (paper 0.804, ours -0.398). The published
  context counts (k = 1, 3, 5) were matched in at most 22 of 57 cells under eight counting
  variants, so those counts were made in a way we did not identify.
- **R2.** Across all 595 pairs of types with at least 5 calls, 52 reach p < 0.05 in file order
  (29.75 expected if independent). After shuffling calls inside every duet the mean is 53.7, so
  order adds nothing. After placing whole duets in random order the mean is 34.1 (5-95%: 25-44),
  p 0.007. The file order, which keeps each pair's duets together, makes the excess. Of the 14
  Table 1 pairs significant in file order, a mean 79.1% stay significant after within-duet
  shuffles. That is just under our registered 80% cut-off, so the registered reading is
  ORDER_SENSITIVE, but only barely. After random placement of duets, 16.7% stay significant.

So the "more than 20 syntactic rules" are correlations of how often call types occur in the same
tenth of a spreadsheet. They depend mostly on which pairs' duets were entered next to each other,
not on the order of calls.

## Priors (Brier)

P1-P7: 6 of 7 came true, Brier 0.158. P6 failed: power of B was 0.105, not at least 0.8. P8
(headline) Brier 0.835: we gave SYNTAX_BEYOND_REPERTOIRE only 0.20 and expected order to fail.
AMENDMENT-1 priors Q1-Q3: Brier 0.472. Q1 came true (Table 1 reproduced). Q2 failed: by the
registered 80% cut-off the published pairs were not order-blind. Q3 failed: the rule count
exceeded random placement of duets.

## Limits

- The call types and the sex of each call are the authors'. Sexes were assigned by the rule
  that female and male calls alternate, female first, so the alternation itself is not tested.
  B tests which female call goes with which male call, and in what order the calls of one sex
  come.
- 52 duets is small, and B had little power for any single weak rule. The 9 surviving
  transitions rest on 3 to 8 occurrences each.
- The order effect could come partly from fixed openers and closers, or from a few pairs.
  AMENDMENT-2 (queued) tests leave-one-pair-out, removal of the repeated duets, a null that
  keeps each call's position class, and the direction of the dependence.
- That sex-specific note types follow a defined order was described for yellow-naped amazon
  duets by [Wright and Dahlin (2007), Behaviour 144:207-228](https://doi.org/10.1163/156853907779947346).
  What is new here is a calibrated test for the warble duets of the 2026 paper, and the finding
  that its published statistic does not measure order.

Paper: Dahlin, Killinger, Snipe, Small, Guenther and Richwine 2026, Journal of Avian Biology
e03552, [doi:10.1002/jav.03552](https://doi.org/10.1002/jav.03552). Data: Dryad
doi:10.5061/dryad.rn8pk0prb (CC0).
