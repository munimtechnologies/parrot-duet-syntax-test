# data/

Authors' data, released under CC0 1.0 on Dryad: Dahlin C. R. et al., "Data from: Decoding parrot
duets: complex communication in yellow-naped amazons", doi:10.5061/dryad.rn8pk0prb (version
421527). Saved from the Dryad page by a person-operated browser on 2026-11-22.

- `Supplement_Data_DRYAD.xlsx`: the authors' file, unchanged. 65,456 bytes, sha256
  bf21a76da9f06a8c1ba02c0bcef608f2301e82b07c20c5f8ad445de86679db8b (the value registered in
  SYNTAX-PREREG.md before download).
- `dryad_sheet01.csv`: its only sheet ('Sheet1', 469 rows including the header), written cell by
  cell with openpyxl and Python's csv module, no other change.
- `DRYAD-README.md`: the authors' README from the same Dryad record (column definitions).

`convert.py` turns `dryad_sheet01.csv` into `calls.csv` (duet, pair, pos, sex, type, label) under
the rules of SYNTAX-PREREG.md, AMENDMENT-1.
