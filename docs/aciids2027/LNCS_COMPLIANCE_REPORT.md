# LNCS / ACIIDS 2027 compliance report

## Venue requirements (call text consulted for ACIIDS 2027, Special Session LR-MSLP)

| Requirement | Status |
|---|---|
| Springer LNCS/LNAI template | `llncs.cls` v2.25 and `splncs04.bst`, unmodified. |
| Absolute limit of 15 pages, including references, figures, tables and appendices | Met: 15 pages. Content runs to p. 13, references to pp. 13–15, and Appendix A (proofs) and B (diagnostic map) to p. 15. |
| Page-length conventions noted in the call | 12–15 pages are standard. Extra pages incur charges, up to a maximum of 25 pages. We are at 15, so no charge. Submission deadline: 31 Oct 2026. |
| Anonymity | Not stated in the call text consulted. The PDF carries placeholders `[AUTHOR NAME(S)]`, `[AFFILIATION, ADDRESS]`, `[E-MAIL]` and `[ORCID]`. **Check the submission system:** fill these in for single-blind review, or anonymise the repository link for double-blind review. |
| Supplementary material | Not stated. Tables S1–S8, Fig. S1 and the implementation details are in a separate 6-page `SelectNorm_ACIIDS2027_Supplement.pdf`. The paper also points to the repository for them. |

## Typesetting checks

| Item | Result |
|---|---|
| Margins, font size, class geometry | Unchanged. No `geometry` package, no `\baselinestretch`, no negative `\vspace`, no `\enlargethispage`. |
| Float placement | Only the standard float parameters were relaxed (`\topfraction` .9, `\bottomfraction` .6, `\textfraction` .1, `\floatpagefraction` .8, `topnumber` 3, `totalnumber` 4). This does not change the page geometry. |
| Font sizes inside floats | Algorithms use `\small` / `\footnotesize`. Tables 1, 2 and 4 use `\footnotesize`. Table 3 (mechanisms, 12 columns) uses `\scriptsize` (7 pt); it could be split if the publisher objects. Body text is 10 pt. |
| Title, running heads, abstract, keywords | Present. The abstract is 220 words (LNCS asks for 150–250). There are six keywords, separated with `\and`. |
| References | `splncs04`, numeric, 34 entries. All are cited, and no reference is undefined. |
| Overfull boxes, undefined references | None in the final log. |
| Fonts | All embedded (`pdffonts`): Type 1 (newtx) plus CID fonts from the Arabic vector snippets. |
| Figures | Fig. 1 (TikZ) and Fig. 3 (pgfplots) are vector and grayscale. Fig. 2 is a vector PDF from matplotlib, with series distinguished by marker and line style as well as colour. |
| Arabic script | Pre-rendered with LuaLaTeX and Amiri (SIL OFL) into vector PDF snippets (`arabic/arabic.pdf`). The main paper compiles with pdfLaTeX, as Springer's production expects. |
| Paper size | pdfLaTeX default, US letter, 612×792 pt. The LNCS text block is unaffected, and Springer re-typesets. Add `\pdfpagewidth=210mm \pdfpageheight=297mm` only if the submission system requires A4. |
| Credits block | `\begin{credits}` with `\discintname`, as the v2.25 template provides. The text is marked "[To be confirmed by the authors.]". |
| Code availability | "Code and Reproducibility" paragraph using `[GITHUB_REPOSITORY_URL]`. No repository was created or pushed. |

## Build

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Arabic snippets need to be rebuilt only if they change: `cd arabic && python3 snippets.py && lualatex arabic.tex`.

## Items for the authors before submission
1. Fill in authors, affiliations, ORCIDs, e-mails and the disclosure statement, or anonymise if required.
2. Replace `[GITHUB_REPOSITORY_URL]` once the repository is public and authorised.
3. Confirm whether ACIIDS accepts a supplementary PDF. If it does not, the repository link carries Tables S1–S8.
4. Fill in Springer's licence-to-publish form; not handled here.
