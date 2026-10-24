# SelectNorm — ACIIDS 2027 (Springer LNCS/LNAI), revision 3

Paper (15 pages, self-contained): `pdflatex main && bibtex main && pdflatex main && pdflatex main`.

Figures 2 and 3 (vector PDF + 300 dpi PNG control images), from this folder:

    python3 figures/figure2_lisible/redraw_figure2_lncs.py          # reads figures/pareto.csv
    python3 figures/figure3_horizontale/build_figure3_data.py       # mechanism_table.csv -> figure3_data_full.csv, checked against the supplied CSV
    python3 figures/figure3_horizontale/redraw_figure3_lncs.py      # reads figure3_data_full.csv

Requirements: Python 3, numpy, matplotlib, DejaVu Sans (matplotlib's bundled font). No path outside this folder is used.
The scripts derive from the supplied `original/redraw_figure2.py` and `original/redraw_figure3_horizontale.py`, kept unchanged in each `original/` folder with the supplied figures and data; only the printed size (4.8 in, the LNCS text width), font and marker sizes and spacing were adapted.
`figures/pareto.csv` and `figures/mechanism_table.csv` are the archived values (written from the run logs by `src/evaluation/figures.py` and the mechanism analysis in the code repository).

Figure 1: `figures/pipeline.tex` (TikZ); `figures/pipeline_standalone.tex` builds it alone.
Arabic snippets (only if changed): `cd arabic && python3 snippets.py && lualatex arabic.tex` (Amiri, SIL OFL).
Technical dossier, not submitted (Tables S1–S8, few-label figure, implementation details): `cd supplement && pdflatex supplement && pdflatex supplement`.

Placeholders: authors, affiliations, ORCID, e-mail, disclosure and AI-use statement, [GITHUB_REPOSITORY_URL].
