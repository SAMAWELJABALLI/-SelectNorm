# Deviations from docs/PROTOCOL.md

## D1 (2026-10-22, after the mE5 main and few-label runs; before any run of the items below)

Observed with mE5 (main run, five seeds): deployable routers (B3, B4, B4b, SelectNorm-src/adapt)
stay within about one macro-F1 point of the better of B0 and B1 on every test set, while the
oracle is 8-14 points higher; the AUC of rho-hat on test disagreements is 0.66 (S3), 0.57 (S4),
0.64 (S5), 0.55 (S6). The few-label setting changes macro-F1 by at most about one point.
A structural point also became clear: at lambda = 0 the factorized Bayes rule reduces to
rho-hat > 1/2, so re-estimating pi on target text cannot change lambda = 0 decisions; pi
matters only for cost-aware operating points (lambda > 0). This is a property of the rule,
not an empirical finding, and the paper states it.

Two extensions are added as **exploratory** and will be reported as such, whatever their outcome:
1. **T_cov** (token-level selectivity): T_cons applied only to tokens with lexical evidence
   (lexicon, negation list or circumfix rule, laughter); tokens that would fall back to the
   character rules stay in Latin script. Motivation: rule fallbacks dominate on Algerian and
   Moroccan input.
2. **Classifier regime "+syn"**: f trained on Arabic-script TSAC plus its synthetic Latin view
   produced by a generator G (reverse TArC lexicon + rules, `src/normalization/generator.py`);
   C and temperature chosen on the Arabic-script dev split plus its G view. Motivation: with an
   Arabic-only f the original Latin view is weak on Tunisian sets, so the routing problem is
   lopsided; a script-augmented f is the usual practice and makes both views competitive.
All other protocol elements (splits, seeds, systems, statistics, thresholds) are unchanged.

## D2 (2026-10-22, analysis only; requested after the mE5 results)

Added `src/evaluation/mechanism.py`, which adds no routing system. It measures the four mechanisms separately:
disagreement detection (AUC of pi, source-trained and label-free target-cross-fitted),
conditional advantage (AUC of rho, source-trained, plus a non-deployable ceiling cross-validated on
target labels), expected benefit (Bayes rule with source rho vs the target-CV ceiling vs the oracle),
and irreducible noise (oracle headroom between two bootstrap-resampled classifiers on the same input).
It is run for every encoder and regime with the default features and with the embedding group.
The archived mE5 metrics computed with encoding-time costs are kept in results/archive/; the rerun
replaces only the cost columns (batch-size-1 latency model), and lambda = 0 decisions are unchanged.

## D3. Container restart during run_all.sh (2026-10-22, ~21:22 UTC)
The container restarted after MARBERTv2 `abl_no_trel`. All earlier outputs were on disk and complete
(1580 rows per routing run, 2500 per adapt run). The three runs not yet started (MARBERTv2 `abl_no_script`,
MARBERTv2 `abl_emb`, mE5 `abl_gbm`) were run afterwards with the identical commands, seeds and data; nothing
was rerun or replaced. Log: logs/run_all_resume.log.

## D4. Major revision (2026-10-22, after internal review)
1. Cost accounting corrected (src/routing/run.py `cost`, `cost_kind`). Before: the normalizer's time
   was added to the avoidable branch cost and entered the Bayes/tuned thresholds; reported costs
   charged every system c0 + g*c1, so B1 was charged two passes. After: f(x) and T(x) are sunk for
   routers, only f(T(x)) is avoidable and enters thresholds; each system is charged for what it runs
   (B0 = c0, B1 = cT + c1, routers = c0 + cT + g*c1, B3 = c0 + g*(cT + c1), R = all).
   Only the `main` tag was re-run (experiments/rerun_cost_fix.sh). Check: all lambda = 0 rows have
   identical macro-F1 and selection (0 of 12,480 changed); 593 lambda > 0 rows changed. Pre-fix
   outputs are archived in results/archive/pre_cost_fix/. Statistics (lambda = 0) are unaffected.
   Ablation/adapt logs keep the old cost field; it is not reported anywhere.
2. Mechanism analysis: 95% bootstrap intervals added (no change to point estimates; verified equal).
3. Noise reference: sensitivity analysis added (src/evaluation/noise_sensitivity.py; 10 pairs per variant).
4. Few-label: separation audit (src/evaluation/check_fewlabel.py); the zero-shot reference in the text
   was the tuned-threshold variant and is now the lambda = 0 Bayes-threshold variant that the
   few-label systems use (range -1.4..+1.5, was -1.2..+1.4).
5. Normalizer intrinsic scores relabelled as development results.

## D5. Second revision (2026-10-23, after the final targeted review)
1. End-to-end timing re-implemented with the real classifier head and live routing (src/evaluation/measured_cost.py);
   the surrogate-head output is archived (results/archive/measured_cost_surrogate_head.json). Live decisions and
   predictions equal the archived ones (0 of 184,400 differ). The first new run overlapped a concurrent audit job;
   mE5 was re-timed alone; both runs kept (measured_cost.json, measured_cost_mE5_retime.json; reported:
   measured_cost_reported.json).
2. Few-label audit replays every sampled index (8,000 draws; ids saved); adapt.py gained an optional --log-samples
   flag (no effect on results); mE5 rerun with logging (tag adapt_audit) is identical to the archived run.
3. Statistics: paired-difference table; post hoc equivalence reading against the 1-point margin. The paper's
   relevance rule (Holm) differs from the protocol's wording (unadjusted interval); identical in the primary regime;
   both reported for +syn.
4. Exploratory: input-dependent cost threshold (src/evaluation/cost_threshold.py).
5. Presentation for the 15-page limit: RQ4 table values moved to text (CSV released); noise table shows ranges
   (per-set CSV released). Previous few-label audit output archived (results/archive/fewlabel_audit_v1.json).
