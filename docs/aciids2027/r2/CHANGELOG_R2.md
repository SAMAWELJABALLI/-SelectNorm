# Revision 2: changelog

Base: `paper_lncs/` (revision 1, 15 pages). That folder is left as it was. The new sources are in `paper_lncs_r2/`.

Result: `main.pdf` has 15 pages, including references and the proofs appendix. The log shows no overfull boxes and no undefined references or citations. A clean rebuild from the zip, which also regenerates Figures 2 and 3 from their scripts, gives the same result.

No experiment was run. No result, protocol, statistical test or exploratory status was changed.

## Figures

### Figure 2 (accuracy–cost trade-off)
- **Layout.** Redrawn as a 2×2 grid (S3 TSAC-Lat, S4 TUNIZI, S5 NArabizi, S6 MYC-Lat) by `figures/fig2_cost_quality.py`.
  - It reads `figures/pareto.csv`, which is the same file used for revision 1's Fig. 2.
  - Outputs are a vector PDF and a 300 dpi PNG control image.
- **Comparators.** All of revision 1's comparators are kept: SelectNorm-adapt with tuned t_λ, SelectNorm-adapt with the Bayes threshold λc̄, B4, B3, B0, B1 and R.
- **Grayscale styling.** The emphasis follows the brief:
  - SelectNorm-adapt (tuned) is solid black with filled circles;
  - B4 is dark grey, dashed, with filled triangles;
  - the Bayes variant and B3 are lighter, with open markers;
  - B0, B1 and R are large single markers.
- **Reference lines.** Grey vertical lines mark the cost of one view (1) and of both views (2).
- **λ endpoints.** The λ = 0 and λ = 0.2 ends of SelectNorm-adapt are labelled with leader lines.
  - The caption states that cost falls as λ rises on every curve. This was checked on all 16 curves.
  - Segments are described as joining discrete settings, not as interpolation.
- **Y-axes.** Each panel has its own vertical axis, and the caption says so.
  - B0 lies far below the routers on S3, S4 and S5, so there it is drawn as a ▼ at the lower edge with its value printed (63.4, 61.5, 63.6).
  - No marker is moved: every point is drawn at its archived (cost, macro-F1).
- **Caption.**
  - Costs are labelled as estimated, and measured timings are reported in the text.
  - Bars are standard deviations over seeds, not confidence intervals.
  - The sunk vs avoidable cost accounting is spelled out.
  - The word "Pareto" was removed from the caption and the text ("trade-off curve"); the LaTeX label `fig:pareto` is internal only.

### Figure 3 (AUC comparison)
- **Content.** This replaces the condensed scatter map. It is a dot plot with intervals (`figures/fig3_auc_dotplot.py`):
  - four panels, one per encoder;
  - rows S3–S6;
  - a common AUC axis with a dashed chance line at 0.5.
- **Series.** Three series per row:
  - AUC(π̂, unlabelled target, cross-fitted);
  - AUC(ρ̂, source labels);
  - AUC(ρ̂, target-trained cross-validated reference).
- **Data and checks.** Values and intervals come from the archived `mechanism_table.csv`. Before plotting, the script checks all 48 point and interval pairs, rounded to two decimals, against Table 3 (`tables/mechanism.tex`) and Table S4 (`tables/mechanism_ci.tex`), and stops on any mismatch. All 48 match.
- **No derived intervals.** No difference interval is computed.
- **Positioning.** Within a row the three series sit at fixed vertical offsets. These are categorical positions only; the AUC positions are exact.
- **Caption.** It states:
  - what π and ρ predict;
  - the different tasks, populations and information access of the three estimators;
  - that intervals exclude estimator refitting;
  - that a gap does not show intrinsic unpredictability.
- **Placement.** The figure now sits in Sect. 6.3 next to the M1/M2 text. The former Appendix B ("Disagreement–Advantage Diagnostic Map") was removed, and its "14 of 16 below the diagonal" statement went with it. Revision 1's map files are kept in `paper_lncs/`.

## Theory
- **Macro-F1 claim.** "accuracy-optimal and only approximately macro-F1-optimal" was replaced. The new text says the Bayes rule minimises the population accuracy–cost objective (Eq. 1) under the stated assumptions, that macro-F1 is evaluated empirically, and that no macro-F1 optimality is claimed.
- **Proposition 1.** Its statement now defines the plug-in router ĝ with the theoretical threshold λc̄ and a known c̄(z). The text after it says that the bound does not cover the tuned-threshold variants t_λ, including the primary system, which are evaluated empirically. No new result was added.
- **"Ceiling" wording.** "target-CV ceiling", "in-domain ceiling" and "even in domain" were replaced by "target-trained cross-validated reference (same features and estimator family)". This applies in:
  - Sect. 5;
  - M2 and M3;
  - the Table 3 caption;
  - the Fig. 3 legend and caption;
  - the Discussion;
  - Limitations, which now adds "not an upper bound on achievable performance".
- **Table headers.** The Table 3 column header (AUC^tgt_ρ) is unchanged.

## Self-contained paper (no supplement at the conference)
- **References removed.** Every pointer to Tables S1, S2, S4, S5, S6 and S7 was taken out of the text and captions. The facts the reader needs are already in the text or are now added:
  - the equivalence interval range against B4;
  - mechanism intervals, now shown in Fig. 3;
  - the noise-reference ranges;
  - the taxonomy summary;
  - the +syn results;
  - the ablations, in a new paragraph.
- **Reproducibility statement.** It no longer mentions supplementary tables.
- **Repository link.** Still the `[GITHUB_REPOSITORY_URL]` placeholder. Remove it, or use an anonymised link, if the review is double-blind.
- **Technical dossier.** The supplement is kept as a working and verification dossier titled "Technical Dossier (not submitted)". Tables S1–S8 are unchanged (`supplement/supplement.pdf`, 6 pages).

## Ablation paragraph (Sect. 6.4, mE5, λ = 0, from Table S7)
| Change | Effect on macro-F1 |
|---|---|
| Always normalising with T_lex instead of T_cons | −4.2 to −6.2 |
| Always normalising with T_rule instead of T_cons | −5.2 to −10.6 |
| Routing over T_lex | 0.6–4.6 points below routing over T_cons |
| T_cov | Fewer disagreements; worse on the Tunisian sets |
| Removing π̂ | At most 0.1, as Sect. 3 implies at λ = 0; presented as a consequence, not a finding |
| Dropping target re-estimation of π̂ | At most 0.2 |
| Removing one feature group | −0.5 to +0.7 |
| Gradient boosting | −0.6 to +0.7 |
| π̂ only or confidence features only | Within 0.2 of always normalising on every set, and 0.6–0.7 below the full router on S6 |

Every figure was recomputed from `tables/ablation.tex` and Table 2.

## Framing and conclusions
- **Introduction.** The contributions are now the six items of the brief: formulation, factorisation, comparison with credible routers, sunk vs avoidable cost, transfer, and the safeguards.
- **Abstract.** Rewritten at 221 words. It states:
  - the formulation;
  - parity with direct-gain deferral (every paired interval within ±0.7);
  - no consistent gain over the better single view;
  - the higher cost;
  - the AUCs;
  - the role of the safeguards;
  - where the bottleneck lies.
- **Removed wording.**
  - "The factorisation adds a diagnosis, not an accuracy gain" became "The factorisation separates disagreement detection from conditional advantage estimation, making their distinct contributions to routing performance measurable", followed by the comparative result.
  - "normalisation is best decided per corpus or dialect" became "The results support corpus- and encoder-specific view selection with a safeguarded normaliser in the evaluated frozen-encoder setting; effects of dialect, corpus, platform, content and normaliser are not isolated."
  - "which about a hundred labels recover" (abstract and conclusion) was removed. The Discussion now says that the set-level result is an average and not a guarantee for every configuration. The text still keeps Proposition 2 (information about b) separate from the final performance.
  - The Sect. 6.3 title "Where per-input routing fails" became "Which factor limits per-input routing".
- **Conclusion.** Rewritten at 124 words, with no promises of future work.
- **Disclosure.** The credits block now includes a sentence on generative AI use, with a placeholder for the authors to complete.

## Space recovered for the figures (nothing scientific removed)
- **Shortened text.** The introduction, related work, setup and RQ3 paragraphs were condensed. The discussion became a single paragraph. Limitations, the Fig. 2 and Fig. 3 captions and the Table 2–4 captions were shortened, keeping all of their information.
- **Removed duplicates.** Each removed sentence is still stated elsewhere:
  - "post-hoc deferral rules estimate B directly" (Formulation) is in Related Work and Setup;
  - the M4 headroom sentence and the Moroccan sign change are in Results;
  - the citations of the transliteration sentence remain in the Introduction;
  - the gradient-boosting range moved to the ablation paragraph;
  - "200 sentences per set" is in Sect. 6.2.
- **Dropped sentence.** "Targeted labels … cannot repair a weak ranking" was removed. It was interpretive; the numbers behind it are in Sect. 6.4.
- **Attribution.** The two corpus URLs in the reproducibility paragraph were replaced by the corpus citations [29] and [22] with their licences. URLs and commits stay in `EXAMPLE_PROVENANCE.md`.
- **Proofs.** The proof headings are now run-in. The content is unchanged; only the wording was tightened.
- **Layout.** No change to margins, font size, line spacing or class geometry. The float parameters are as in revision 1.

## Tables
- Tables 1–4 keep their values, rows, columns and numbering. The `tables/` files are byte-identical to revision 1, except for the Table 4 caption, which was shortened.
- Tables S1–S8 are unchanged in `tables/` and in the technical dossier.
