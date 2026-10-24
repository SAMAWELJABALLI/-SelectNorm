# Editorial changelog: ACL-style manuscript to ACIIDS 2027 (LNCS/LNAI)

Source: `paper/` (validated manuscript, commit 20c130b). Target: `paper_lncs/`, Springer `llncs.cls` v2.25 with `splncs04.bst`, 15 pages including references and appendix.

The experimental protocol, algorithms, results, numbers, tests and conclusions are unchanged. See `SCIENTIFIC_INTEGRITY_CHECK.md`.

## Template conversion
- The two-column ACL layout became single-column LNCS (`\documentclass[runningheads]{llncs}`). No change to margins, font size or class geometry. Only LaTeX float-placement parameters (`\topfraction`, `\textfraction`, `\floatpagefraction`, float counters) were relaxed.
- `\cref` was replaced by LNCS-style `Table~\ref`, `Fig.~\ref`, `Sect.~\ref` and `Eq.~(\ref)`. Natbib `\citep`/`\citet` became numeric `\cite`.
- The title is the one specified in the brief. Its US spellings ("Factorized", "Normalization") were kept as given. The body uses British -ise spelling throughout; a grep of the text found no remaining -ize, "unlabeled" or "modeling" forms.
- The running title is "SelectNorm: Disagreement-Factorised Per-Input Normalisation".
- Authors, affiliation, ORCID and e-mail are placeholders. None were invented.
- Keywords were added: Arabizi, Transliteration, Selective normalisation, Learning to defer, Frozen encoders, Dialect transfer.
- An LNCS `credits` block was added with a disclosure statement marked "[To be confirmed by the authors.]".

## Deleted redundancy (about 5,900 → 4,300 words in the main sections)
- **Introduction.** Motivation and the RQ list were condensed, and the contributions shortened to four bullets. The negative headline result is kept in the last sentence.
- **Related work.** Regrouped into four themes. Every original citation is kept, and none was added (the same 34 keys are cited).
- **Setup.** Five compact paragraphs. The details of the ACL reproducibility appendix (encoder revisions and licences, the C grid, the 17 router features, the few-label audit, per-example exports) moved to the supplementary PDF, section "Implementation details", verbatim apart from spelling.
- **Results.** Repetitions between the text and the tables were removed. Every reported number remains, either in the text or in a table.
- **Supplementary tables.** Nine items moved to `SelectNorm_ACIIDS2027_Supplement.pdf` with unchanged values: paired differences (S1), +syn (S2), routing (S3), mechanism intervals (S4), noise sensitivity (S5), taxonomy (S6), ablation (S7), intrinsic accuracy (S8) and the few-label figure (S1 there).
- **Proofs.** Condensed to their essential steps in Appendix A. The statements are unchanged.

## Rewritten prose
- Shorter sentences, and filler words removed. A grep for "notably, importantly, crucial, robust, interestingly, it is worth noting, to the best of our knowledge" finds nothing.
- The status of each analysis (pre-specified, exploratory, added in revision) is stated in one paragraph (Sect. 5, "Status of analyses").
- **Conclusion.** Rewritten at 117 words, with no future-work promises.
- **Code and Reproducibility.** A statement was added using the placeholder `[GITHUB_REPOSITORY_URL]`. No real URL was invented.

## Figure improvements
- **Fig. 1, pipeline.** Redrawn in grayscale TikZ (`figures/pipeline.tex`, plus a standalone PDF).
  - Separate inference and offline lanes.
  - c0 and cT marked as sunk; the second pass c1 marked as avoidable and dashed.
  - Few-label shift shown as an optional dashed box.
- **Fig. 2, Pareto.** Re-laid out as a 1×4 strip for the single-column page (`src/evaluation/figures.py --lncs`). It uses the same CSV as the ACL version.
- **Fig. 3, Disagreement–Advantage Diagnostic Map (Appendix B, new).**
  - Plots AUC of π̂ against AUC of ρ̂, using archived values and intervals only (`figures/diagnostic_map.py`, `.csv`, `.tex`).
  - Encoder is shown by marker shape and corpus by grey fill.
  - Includes chance lines and a y = x line.
- **Algorithms.** Algorithm 1 (normaliser), Algorithm 2 (training) and Algorithm 3 (inference) were checked line by line against `src/routing/policies.py` and `src/normalization/arabizi.py`. Algorithms 2 and 3 are set side by side.
- **Arabic script.** Rendered with LuaLaTeX and the Amiri font into vector snippets (`arabic/`), so the main file still compiles with pdfLaTeX.

## Examples added (Table 4, Option B)
- Six mE5 test sentences: two TSAC, two NArabizi and two MYC.
  - The TSAC and NArabizi text is quoted verbatim, with the normaliser output.
  - The MYC text is withheld because MYC has no licence; the table describes the phenomenon instead.
- Gold label, p0, p1 and the per-seed routing and prediction come from the archived exports.
- The table and the limitations section both state that the examples are hand-picked. Provenance is in `EXAMPLE_PROVENANCE.md`.

## Unresolved issues for the authors
1. Author names, affiliations, ORCIDs, e-mails and the disclosure statement are placeholders.
2. `[GITHUB_REPOSITORY_URL]` must be replaced once the repository is authorised. Nothing was pushed.
3. ACIIDS 2027 rules on supplementary material and anonymity were not stated in the call text consulted. Check whether the supplement can be submitted, or whether the repository link must be anonymised.
4. NArabizi sentiment labels (Touileb et al.) state no licence. Only the UD text (CC BY-SA 4.0) is quoted.
5. The diagnostic map is small (3.9 cm high) to keep 15 pages. A larger version is in the standalone PDF.
6. The title keeps US spelling while the body is British. Harmonise the title if desired.
