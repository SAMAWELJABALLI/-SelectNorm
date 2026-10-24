# SelectNorm — ACIIDS 2027 (Springer LNCS/LNAI), revision 2

Paper (15 pages, self-contained): `pdflatex main && bibtex main && pdflatex main && pdflatex main`.

Figures 2 and 3 (vector PDF + 300 dpi PNG control images), from this folder:

    python3 figures/fig2_cost_quality.py   # reads figures/pareto.csv
    python3 figures/fig3_auc_dotplot.py    # reads figures/mechanism_table.csv, checks values against tables/mechanism.tex and tables/mechanism_ci.tex, writes figures/fig3_auc.csv

Requirements: Python 3, pandas, matplotlib (TeX Gyre Termes font optional). No path outside this folder is used.
`figures/pareto.csv` and `figures/mechanism_table.csv` are the archived values (written from the run logs by `src/evaluation/figures.py` and the mechanism analysis in the code repository).

Figure 1: `figures/pipeline.tex` (TikZ); `figures/pipeline_standalone.tex` builds it alone.
Arabic snippets (only if changed): `cd arabic && python3 snippets.py && lualatex arabic.tex` (Amiri, SIL OFL).
Technical dossier, not submitted (Tables S1–S8, few-label figure, implementation details): `cd supplement && pdflatex supplement && pdflatex supplement`.

Placeholders: authors, affiliations, ORCID, e-mail, disclosure and AI-use statement, [GITHUB_REPOSITORY_URL].
