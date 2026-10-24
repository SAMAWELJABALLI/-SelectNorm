# Revision 2: point-by-point response

**1. Scope and constraints.**
- I read the whole manuscript before making any change.
- Revision 1 is untouched (`paper_lncs/`); revision 2 is in `paper_lncs_r2/`.
- The template, margins, font size and line spacing are unchanged.
- The paper is 15 pages, including references and the appendix.
- Tables 1–4 keep their values, rows, columns and numbering; only captions were shortened.
- Tables S1–S8 are preserved.
- No training was run, and no result, protocol, test or exploratory status was changed.

**2. No supplementary material at the conference.**
- Every reference to Tables S1–S8 has been removed from the paper.
- The essential elements are now in the text or figures:
  - equivalence intervals against B4;
  - mechanism intervals (Fig. 3);
  - the noise-reference ranges;
  - the taxonomy summary;
  - the +syn results;
  - the ablations.
- The supplement is kept as a "Technical Dossier (not submitted)".
- The repository sentence still uses the `[GITHUB_REPOSITORY_URL]` placeholder. Delete it, or anonymise the link, if the review is double-blind. Nothing was published and no repository was created.

**3. Contributions.**
- The introduction now lists the six contributions you specified.
- The abstract, Discussion and Conclusion state what the results establish:
  - SelectNorm is on par with direct-gain deferral;
  - it does not consistently beat the better single view;
  - routing costs more than either single view;
  - the bottleneck is the conditional advantage;
  - the safeguards matter more than the routing components.
- The diagnosis sentence was replaced with the formulation you proposed, followed by the comparative result.
- No superiority claim was added.

**4. Figure 2.**
- Redrawn as a 2×2 grid in grayscale, with all comparators kept.
- Visual priority goes to SelectNorm (tuned), B4, B0/B1 and R.
- The λ = 0 and λ = 0.2 ends are labelled.
- Vertical lines mark the cost of one view and of both views.
- The caption covers:
  - estimated costs, with measured timings given in the text;
  - bars as standard deviations over seeds;
  - the sunk vs avoidable cost accounting;
  - that segments are not interpolations;
  - that the vertical axes differ between panels;
  - that B0 is marked at the panel edge when it lies outside the range.
- The data are unchanged and no marker was offset. "Pareto" is no longer used.

**5. Figure 3.**
- Redrawn as a dot plot with horizontal intervals:
  - four panels, one per encoder;
  - rows S3–S6;
  - a common AUC axis with a chance line.
- It shows three series: π̂ on the target, ρ̂ from source labels, and the target-trained cross-validated reference.
- All 48 values and intervals are checked automatically against Tables 3 and S4.
- No difference interval is computed.
- The caption explains the three estimators, the differences in information access and the interval scope, and warns that a gap between the AUCs is not evidence of intrinsic unpredictability.
- The figure moved to Sect. 6.3, and the former Appendix B was removed.

**6. Macro-F1 optimality.** The "approximately macro-F1-optimal" claim was removed. The text now says that the rule minimises the accuracy–cost objective under the stated assumptions, that macro-F1 is evaluated empirically, and that no macro-F1 guarantee is claimed.

**7. Proposition 1.**
- It is now stated for the plug-in router with threshold λc̄ and known c̄(z).
- The text says it does not cover tuned t_λ, and that those variants are evaluated empirically.
- No new bound was added.

**8. "Ceiling".**
- Replaced everywhere by "target-trained cross-validated reference (same features and estimator family)": text, Table 3 caption, Fig. 3 and Limitations.
- Limitations adds "not an upper bound on achievable performance".
- Table data and headers are unchanged.

**9. Ablations.** Sect. 6.4 has a new paragraph covering:
- the safeguards (−4.2 to −10.6 without them);
- the small effect of the routing components;
- π̂ at λ = 0, presented as a consequence of Sect. 3;
- the label-free simplifications, including where they are worse (S6).

Every figure in it was rechecked against the ablation table.

**10. Practical conclusions.**
- Now reads: "corpus- and encoder-specific view selection in the evaluated frozen-encoder setting", with confounding factors stated.
- The label result is described as an average with no guarantee for every configuration.
- Proposition 2 is still described as concerning information about b, not final accuracy.

**11. Style.**
- British English throughout.
- No filler words; the greps are clean.
- Citations are unchanged (the same 34 keys).
- An AI-use sentence was added to the disclosure block, with a placeholder for you to complete.

**12. Figure reproducibility.**
- `figures/fig2_cost_quality.py` and `figures/fig3_auc_dotplot.py` read CSVs inside the zip and use relative paths.
- Each writes a vector PDF and a 300 dpi PNG.
- The commands are in the README.
- I rebuilt the paper from the unzipped archive after deleting the figure PDFs: 15 pages, no errors.

**13. Fifteen pages.**
- Space came from removing repetition and shortening captions. Each removed duplicate is still stated elsewhere; see the changelog.
- No table, unfavourable result or necessary caveat was removed.
- One interpretive sentence ("targeted labels cannot repair a weak ranking") was dropped.

**14. Checks.**
- Tables are preserved.
- Figures match the exports (automatic check for Fig. 3, the same CSV for Fig. 2).
- 15 pages.
- No overfull boxes and no undefined references or citations.
- Figures were inspected at full size: no overlaps; labels were moved where needed.
- The theory and the implementation description are consistent: the tuned and Bayes thresholds are stated in Sect. 4 Module C and Sect. 5.
- Nothing essential depends on the dossier.
