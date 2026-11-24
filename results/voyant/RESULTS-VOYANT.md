# RESULTS-VOYANT

T: Table 1 has 23 rows (8 pair a call type with itself, r = 1 by definition; 19 positive). Numbers of observations n in 3-100 for which every published p equals the p of its r: [10].

R1 (10 bins, file order): best variant all_raw, reading **REPRODUCED**.

| variant | rows compared | median abs diff r | max abs diff r |
|---|---|---|---|
| all_raw | 15 | 0.000 | 1.202 |
| all_rel | 15 | 0.003 | 1.203 |
| noUnknown_raw | 15 | 0.010 | 1.201 |
| noUnknown_rel | 15 | 0.014 | 1.200 |

| context-count variant | published cells matched exactly |
|---|---|
| all_right_stream | 22 of 57 |
| all_right_within | 16 of 57 |
| all_both_stream | 21 of 57 |
| all_both_within | 11 of 57 |
| noUnknown_right_stream | 21 of 57 |
| noUnknown_right_within | 15 of 57 |
| noUnknown_both_stream | 21 of 57 |
| noUnknown_both_within | 11 of 57 |

| term 1 | term 2 | r paper | r ours | p ours |
|---|---|---|---|---|
| Scree | Scree | 1.000 | 1.000 | 0.0000 |
| CCall | CCall | 1.000 | 1.000 | 0.0000 |
| Julia | Julia | 1.000 | 1.000 | 0.0000 |
| D | D | 1.000 | 1.000 | 0.0000 |
| B | B | 1.000 | 1.000 | 0.0000 |
| C | C | 1.000 | 1.000 | 0.0000 |
| M | M | 1.000 | 1.000 | 0.0000 |
| U1 | U1 | 1.000 | 1.000 | 0.0000 |
| U1 | U2 | 0.986 | 0.986 | 0.0000 |
| M | Z | 0.874 | 0.874 | 0.0009 |
| B | Ha | 0.859 | 0.859 | 0.0015 |
| C | U1 | 0.814 | 0.814 | 0.0041 |
| C | O | 0.804 | -0.398 | 0.2540 |
| C | U2 | 0.784 | 0.784 | 0.0073 |
| J | K | 0.746 | 0.746 | 0.0132 |
| Mirror M | M | 0.740 | 0.740 | 0.0145 |
| Scree | Yoohoo | 0.685 | 0.685 | 0.0288 |
| K | M | 0.663 | 0.663 | 0.0367 |
| Mirror M | Z | 0.642 | 0.642 | 0.0454 |
| Scree | Z | -0.635 | -0.635 | 0.0486 |
| B | Mirror M | -0.638 | -0.638 | 0.0472 |
| B | U2 | -0.641 | -0.641 | 0.0458 |
| M | Scree | -0.667 | -0.667 | 0.0350 |

R2 (all_raw; 468 tokens, 37 types, 35 with >= 5 tokens; 595 type pairs tested):
- 'rules' (p < 0.05 at n = 10) in file order: 52 (35 positive); 29.8 expected if independent
- mean rules after shuffling call order inside every duet: 53.7
- mean rules under random placement of whole duets: 34.1 (5-95%: 25-44); p_placement = 0.007, reading **EXCESS_AT_BIN_SCALE**
- Table 1 pairs (different types) significant with the published sign in file order: 14 of 15; mean share still significant after within-duet shuffles: 0.791, reading **ORDER_SENSITIVE**; after random placement: 0.167

Priors: Q1_REPRODUCED True, Q2_ORDER_BLIND False, Q3_CHANCE_LEVEL False; Brier 0.472.

Made with AI agents working in MV2's name; not checked by a human expert.
MV2, Munim, Inc., mv2@munimtech.com
