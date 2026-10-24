# Change log of the revision, by manuscript section

| Section | Change | Reason |
|---|---|---|
| Title | "A Disagreement-Factorized Analysis of Per-Input Normalization for Arabizi with Frozen Encoders" | A3, A7 |
| Abstract | Rewritten: elementary identity used as analysis device; cost statement corrected (routing costs more than a single view); AUC ranges; noise statement as a reference; frozen-encoder scope | A1, A3, A4, A7, C1-C2 |
| 1 Introduction | Identity called elementary (QBC); evaluation contribution says "latency-based costs checked by end-to-end timing" instead of "measured costs"; contributions recast around the analysis and the limits of conditional-advantage prediction; normalizer contribution states development-only evaluation; scope sentence | A2, A3, A7, B1 |
| 3 Formulation | Costs split into c0, cT (sunk) and c1 (avoidable); risk and Bayes rule rewritten; consequence for comparisons with single views; factorization paragraph titled "elementary"; regret bound and Fisher-information proposition described as standard | A1, A3 |
| 4 Method, Fig. 1 | Figure marks sunk vs avoidable costs and the offline lane; Module C states only the avoidable cost enters the threshold; complexity paragraph names the avoidable term; Alg. 3 input renamed | A1, A8 |
| 5 Setup | New "Few-label setting" paragraph (fold-separated labels, audit); mechanism paragraph: noise comparison is a reference, intervals described (seed-averaged bootstrap, no refitting); cost metric charges each system for what it runs | A4, A5, A6, A1 |
| 6.1 Main results, Table 2 | Table split into panels, primary system shaded, new markers; numbers unchanged | A8 |
| 6.2 Cost, Fig. 2 | Figure regenerated with corrected costs; axis and caption say "estimated cost"; text rewritten: routing never cheaper than a single view; saving only vs two-view ensemble; end-to-end measured costs summarized | A1, B1-B3 |
| 6.3 Mechanisms, Table 3 | Interval marks added; M1-M3 text cites intervals; M4 rewritten as a reference with sensitivity | A4, A6 |
| 6.4 Few labels, Fig. 3 | Zero-shot reference corrected (-1.4..+1.5); explicit ticks | A5, A8 |
| 7 Discussion | Noise wording, scope of the analysis to other settings, recommendations restricted to frozen encoders; cost recommendation reversed | A4, A7, C1 |
| Limitations | Scope sentence; normalizer not independently validated; analysis-interval caveat | A2, A6, A7 |
| App. A Proofs | Bayes-rule proof includes the sunk term | A1 |
| App. B Normalizer | Retitled "development results"; caption states tuning on the split and the audit results | A2, B4 |
| App. C (new) | Mechanism intervals table; noise-reference sensitivity table | A4, A6 |
| App. D Reproducibility | Cost definitions (measured vs estimated); end-to-end measured costs; few-label audit; per-example exports and stand-alone test script | B1, B5, A5 |
| App. E Additional results | Routing table regenerated with corrected costs, set as one wide table; +syn table in panel layout; encoder revisions table folded into the text (same content) to stay within 15 pages | A1, A8 |

Code and data
- src/routing/run.py: `cost()`, `cost_kind()`; `c1` no longer includes normalizer time; `ct` separate.
- src/evaluation/mechanism.py: `--ci` bootstrap intervals (point estimates unchanged).
- New: src/evaluation/noise_sensitivity.py, src/evaluation/check_fewlabel.py,
  src/normalization/audit_tarc.py, src/evaluation/measured_cost.py,
  src/evaluation/export_predictions.py, scripts/reproduce_stats.py,
  experiments/rerun_cost_fix.sh, experiments/revision_analyses.sh.
- src/evaluation/tables.py, figures.py: panel table, interval marks, interval and noise tables, ticks, cost axis label.
- Archived pre-fix outputs: results/archive/pre_cost_fix/.

## Second revision (2026-10-23)

| Section | Change | Reason |
|---|---|---|
| Abstract, 1 | Bounded similarity claims; mechanism limit restricted to features/estimators tested | A3, A4 |
| 5 Setup | Seeds definition; relevance rule vs protocol wording; non-significance is not equivalence; "Status of analyses" paragraph; few-label audit sentence and S5 k=128 budget | A2, A4, A5 |
| 6.1 | Paired differences with intervals (Table 7); post hoc equivalence vs B4; inconclusive vs B1/B3; LaBSE MYC loss vs B0 stated | A4 |
| 6.2 | End-to-end numbers from the real pipeline; input-dependent cost sentence | A1, A5 |
| 6.3 | M2/M3 qualified to features and estimators | A3 |
| 6.5 | RQ4 numbers in text; +syn gains and losses under both relevance rules | A4, space |
| 7, Limitations | Qualified mechanism statement; "at or below chance"; recommendation (iv) mentions losses; post hoc equivalence caveat; protocol sentence corrected | A3, A4, A5 |
| App. A/B | Paired-difference table; few-label audit, exports, input-dependent cost and cost-check paragraphs rewritten; noise table as ranges; RQ4 table removed (CSV); empty section headings removed; appendix in \small | A1, A2, A5 |

Code: src/evaluation/measured_cost.py (rewritten), src/evaluation/check_fewlabel.py (rewritten),
src/routing/adapt.py (--log-samples), src/evaluation/cost_threshold.py (new), src/evaluation/tables.py
(paired_table, compact noise table), experiments/revision2_checks.sh (new).
