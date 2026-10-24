#!/bin/sh
# Build the R3 manuscript (pdfLaTeX + BibTeX, Springer llncs). Output: paper/main.pdf.
# The Arabic snippets are pre-rendered (paper/arabic/arabic.pdf); rebuild them only if changed:
#   cd paper/arabic && python3 snippets.py && lualatex arabic.tex
set -e
cd "$(dirname "$0")/../paper"
run() { "$@" >/dev/null || { echo "failed: $*"; tail -40 main.log 2>/dev/null; exit 1; }; }
run pdflatex -interaction=nonstopmode -halt-on-error main
run bibtex main
run pdflatex -interaction=nonstopmode -halt-on-error main
run pdflatex -interaction=nonstopmode -halt-on-error main
pages=$(pdfinfo main.pdf 2>/dev/null | awk '/^Pages/{print $2}')
if grep -E 'undefined|Overfull|Missing character' main.log; then echo 'build warnings above'; exit 1; fi
echo "paper/main.pdf: ${pages:-?} pages"
