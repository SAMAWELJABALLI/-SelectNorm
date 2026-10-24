# Scientific integrity check: ACIIDS 2027 version

Compared against the validated manuscript `paper/` at commit 20c130b and the archived results under `results/`. No experiment was re-run to produce a new result. The normaliser was re-run once, only to confirm the outputs quoted in Table 4.

## Numbers
- The numeric tokens of the LNCS sections, tables and preamble (630 distinct) were extracted automatically and matched against the ACL sources.
- 602 occur verbatim. The other 28 fall into four groups:
  - Table 4 values (p0, p1, per-seed routing and predictions, corpus line and row numbers). These were checked against `results/qualitative/examples_mE5.json` and `results/export/per_example`.
  - "[0.57, 0.77]" (envelope of the M1 intervals). Written "between 0.57 and 0.77" in the ACL text, and recomputed from `paper/tables/mechanism_table.csv` as 0.574–0.771.
  - Layout dimensions and the class version (0.555, 6.65, 2.25).
  - The year 2027.
- Tables 2 and 3 and the supplementary tables are the archived table files. Only the spelling of row labels was changed (normalize → normalise, unlabeled → unlabelled).
- The diagnostic map (Fig. 3) is generated from `paper/tables/mechanism_table.csv` (columns `auc_pi_tgt`, `auc_rho_src` and their intervals). The script and CSV are included.

## Protocol, algorithms, statistics
- Splits, systems, threshold tuning (policy development split only, never a test set), the paired bootstrap (10,000 resamples), Holm correction over 20 comparisons and the 1-point relevance margin are unchanged.
- Algorithms 1–3 were checked against the code:
  - equal-weight π̂ on P ∪ U;
  - MAP shift with an N(0,1) prior;
  - normaliser branch order: laughter, foreign/context, negator list, lexicon, ma…ch, rules.
- Propositions 1 and 2 keep their statements; the proofs are only condensed.

## Distinctions preserved
- **Pre-specified vs exploratory.** Stated in Sect. 5 ("Status of analyses"). The exploratory items (+syn, T_cov, M1–M4, input-dependent cost) are labelled where they appear.
- **Estimated vs measured cost.** Fig. 2 and the cost text say "estimated". The timing check is reported separately as measured: B0 22–31 ms; B1 0.91–1.05; SelectNorm 1.31–1.97; R 1.91–2.07; all 184,400 live decisions reproduced.
- **Descriptive similarity vs formal equivalence.**
  - The B4 intervals within [−0.63, +0.58] are called "a post hoc equivalence reading".
  - The targeted vs random difference is "descriptive".
  - The set-level choice comparison is "descriptive".
  - "Non-significance is not read as equivalence" is retained.

## Negative results and limitations retained
- No learned router consistently beats the better single view, and routing costs more than either view. This appears in the abstract, the introduction, the results and the conclusion.
- The relevant losses are kept:
  - XLM-R MYC −3.8;
  - LaBSE MYC −2.5 vs B0;
  - +syn MYC −2.4 and −1.8;
  - worse than B4 once (−0.4).
- Weak ρ̂: AUC 0.54–0.71, with XLM-R S5/S6 at or below chance; target-CV 0.53–0.68.
- The few-label effect is near zero (−1.4 to +1.5, mean −0.01), and targeted labels give no advantage.
- **Limitations section.** All ACL items are kept:
  - task scope, including the K-class remark;
  - restriction to frozen encoders with linear heads;
  - normaliser not independently validated;
  - data confounds, not attributed to dialect alone;
  - licences;
  - development with an inspected n-gram classifier;
  - mechanism-interval scope;
  - post-features not studied;
  - post hoc equivalence;
  - cost-model scope.
- One addition: the qualitative examples are hand-picked.
- The "Explanations" paragraph keeps the caveat that other features, fine-tuned representations or estimators might do better, and that unpredictability is not shown to be intrinsic.

## Novelty
- No new methodological claim. The factorisation is described as "elementary" and linked to query-by-committee.
- The contributions are framed as an analysis, an evaluation and a conservative normaliser.

## Citations
- The same 34 citation keys as the ACL version. Nothing was added or removed.
- Corpus and repository URLs appear only in the Code and Reproducibility paragraph, not as bibliography entries.

## Qualitative examples
- Only genuine corpus sentences. None were paraphrased or invented.
- The MYC text is withheld; see `EXAMPLE_PROVENANCE.md`.
