# SelectNorm — ACIIDS 2027 (Springer LNCS/LNAI) sources

Build: `pdflatex main && bibtex main && pdflatex main && pdflatex main` (15 pages).
Supplement: `cd supplement && pdflatex supplement && pdflatex supplement` (uses figures/fewlabel.pdf).
Arabic snippets (only if changed): `cd arabic && python3 snippets.py && lualatex arabic.tex` (Amiri, SIL OFL, in arabic/fonts).
Figures: pipeline.tex (TikZ), diagnostic_map.py -> diagnostic_map.{csv,tex} (pgfplots), pareto_lncs.pdf from src/evaluation/figures.py --lncs; *_standalone.tex build each figure alone.
Placeholders to fill: authors, affiliations, ORCID, e-mail, disclosure statement, [GITHUB_REPOSITORY_URL].
DescriptionTexts.txt: alt-texts written by llncs.cls from \Description.
