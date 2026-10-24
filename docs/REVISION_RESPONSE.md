# SelectNorm: response to the review and record of the revision

Date: 2026-10-22. Two requests are answered here: the eight reviewer findings (part A) and the
targeted cost-accounting and reproducibility correction (part B). Part C lists every claim that
changed, part D the change log by manuscript section, and part E the threats to validity that
remain. Nothing in the experimental protocol (data, splits, seeds, systems, metrics, primary
comparisons, decision rule) was changed; the corrections and every re-run are listed below and
in docs/DEVIATIONS.md (D4).

## A. Reviewer findings

**A1. Cost formulation.** *Agreed; this was an error.* The normalizer runs, and its metadata
feeds the router, before `g` is decided, but the code added its time to the conditional branch
cost `c1`. Worse, reported costs charged every system `c0 + g*c1`, so "always normalize" (B1)
was charged two passes although it runs only `T(x)` and `f(T(x))`.
Correction: the risk is now `E[e_g + lambda (c0 + cT + c1 g)]`; `c0 + cT` is sunk and drops out,
so the Bayes rule is `g* = 1[B(z) > lambda * E[c1|z]]` with `c1` the second pass only
(Section 3, Eq. 1-2, proof in App. A). Each system is charged for what it runs
(`src/routing/run.py::cost`): B0 `c0`; B1 `cT + c1`; learned routers `c0 + cT + g c1`;
B3 `c0 + g (cT + c1)`; random `(1-g) c0 + g (cT + c1)`; R `c0 + cT + c1`.
Re-run: only the `main` routing runs (the only ones whose costs or lambda > 0 points are
reported), all 8 backends, same seeds. Verified: all lambda = 0 rows (macro-F1, selection) are
identical, 0 of 12,480 changed; 593 lambda > 0 rows changed. The paired tests use lambda = 0
only and are unaffected. Pre-fix outputs: results/archive/pre_cost_fix/.
Effect on claims: see C1-C2. The efficiency claim is withdrawn.

**A2. Normalizer evaluation leakage.** *Agreed.* No independent transliteration test set exists
for us: the TArC 20% split was used to design the safeguards, and NArabizi scores were computed
during development. We relabel all intrinsic numbers as development results (App. B title,
table header and caption; intro contribution 4; Limitations) and make no claim of independent
validation. We also audited the split (B4 below) to bound the optimism.

**A3. Novelty.** *Agreed.* The factorization is now called elementary and related to
query-by-committee; the regret bound is described as the standard plug-in argument; the
Fisher-information proposition as a one-line calculation about estimating the shift, not about
router accuracy. The contribution is stated as a disagreement-factorized *analysis* and the
empirical evidence on the limits of conditional-advantage prediction (title, abstract,
intro, Section 3). No new theoretical result is claimed.

**A4. Oracle noise control.** *Agreed.* The bootstrap comparison is now called a reference and
explicitly "a diagnostic, not a decomposition" (Section 5 mechanism paragraph, Section 6.3 M4,
Discussion). New sensitivity analysis (App. C, Table "noise"; `src/evaluation/noise_sensitivity.py`,
10 pairs per variant): the reference ranges 3-15 points with bootstrap resampling, 2-6 with 80%
subsamples, 2-15 with 50% subsamples, 2-11 with C/3 and 5-22 with 3C. Because it moves by this
much, the paper no longer says how much of the views' headroom is noise or is recoverable; it
says only that headroom of this size arises from training-sample variability alone, so oracle
headroom is a weak indicator of what a router can gain. The earlier wording "much of the oracle
headroom is noise" is withdrawn (C4).

**A5. Few-label separation.** *Verified, and documented.* Each test set is split into two
folds by source sentence; labels used to adapt the router, re-tune B3, re-fit B4 or choose
B0/B1 for fold f are drawn only from the other fold, so no sentence's label informs its own
prediction. `src/evaluation/check_fewlabel.py` replays all 1,000 label draws and found no
overlap (results/statistics/fewlabel_audit.json). The protocol is now described in Section 5
("Few-label setting") and App. D. One reporting inconsistency was corrected: the "zero-shot"
reference for the few-label change used the tuned-threshold variant while the few-label systems
use the lambda = 0 Bayes threshold; with the matching reference the change is -1.4 to +1.5
points (mean -0.01), previously reported as -1.2 to +1.4 (mean +0.05) (C5).

**A6. Uncertainty for mechanism measurements.** *Done.* 95% percentile intervals from 1,000
bootstrap resamples of test sentences for AUC(pi), AUC(rho) source and target-CV, the
calibration gap, and the M3 gains. Repeated measurements: each resample reweights the sentences
of all five seeds with the same counts and averages the statistic over seeds. Estimators are
not refitted, so intervals cover evaluation sampling only (stated). Table 3 marks AUCs whose
interval contains 0.5 and gaps/gains whose interval excludes 0; App. C gives all intervals.
Point estimates are unchanged (verified). Paired testing for the main comparisons is unchanged.

**A7. Scope.** *Done.* "Frozen encoders" is in the title; the abstract, intro, discussion
recommendations and Limitations restrict conclusions to frozen encoders with linear heads and
binary sentiment; the claim that the analysis "applies to" other two-view settings is replaced by
"the same measurements can be made ... we have not done so".

**A8. Presentation.** Table 2 is split into two panels of two encoders, set at \small, with the
primary system shaded and clearer significance markers. Figure 3 has explicit ticks
8/16/32/64/128. Figure 1 marks the sunk costs (c0, cT), the avoidable cost (c1) and the
offline training lane ("no inference cost").

## B. Cost-accounting and reproducibility correction

**B1. Cost definitions; measured vs estimated latency.** Fixed as in A1. The per-sentence encoder
costs used in all runs are *estimated*: a per-encoder model a + b*tokens fitted to measured
batch-1 latencies of 300 sentences per set and view (R^2 0.51-0.68), plus the normalizer time
*measured* per sentence. This is now stated (App. D, Costs). New end-to-end measurement
(`src/evaluation/measured_cost.py`): each system is executed as deployed on 200 random sentences
per test set and encoder, systems timed back to back in rotating order. Results
(results/metrics/measured_cost.json, App. D "Costs"): measured B0 takes 23-30 ms per sentence, 0-4 ms
more than estimated; measured relative costs are B1 0.91-1.04, SelectNorm-adapt 1.32-1.98 and
R 1.92-2.07 passes. They differ from the estimates by -0.02 to +0.03 for B1 and R and by +0.04
to +0.07 for SelectNorm, whose feature computation the token model does not include. The measured
numbers therefore confirm the corrected conclusion (C1) and make it slightly stronger. A first
measurement run with a short warm-up inflated the first sets timed (e.g. mE5 S3 B0 70 ms); it was
discarded and archived (results/archive/measured_cost_short_warmup.json) before the rerun with a
300-sentence two-view warm-up; the warm-up change is the only difference between the two runs.
Wording: every cost in Figure 2 and Table 9 is now called *estimated* (axis label, captions,
Section 5 metric, Section 6.2, App. D, Limitations); "measured" is used only for the normalizer
time and the end-to-end check.

**B2. Bayes threshold; affected analyses.** Threshold uses the avoidable cost only (A1). Re-run:
`main` routing for 8 backends (experiments/rerun_cost_fix.sh). Regenerated: Figure 2 (accuracy-cost),
Table 9 (routing behaviour, cost column; now one wide table), all cost statements in text. Not affected: every
lambda = 0 result, Table 2, all paired tests, mechanism analysis, few-label results (lambda = 0),
ablations (lambda = 0).

**B3. Accuracy-cost figure and efficiency claims.** Figure 2 regenerated with corrected costs and
caption stating what each system is charged. Changed claims: C1, C2.

**B4. TArC audit** (`src/normalization/audit_tarc.py`, results/metrics/tarc_audit.json).
(i) The 80/20 split (3,838/960 sentences) matches the saved ids; the lexicon is built from the
80% part only. (ii) Of the 29 hand-listed words (negators, context-ambiguous function words),
none occurs only in the held-out part; one ("lee") occurs in neither. (iii) Held-out word accuracy
of T_cons is 69.1% on all tokens and 65.8% on the 87% of tokens no hand list or regex touches.
(iv) Swapped split (lexicon from the 20%, metrics on the 80% that was never inspected for rule
design): negation preserved 94.4% (development: 96.1%), French/English protection
precision/recall 95/77 (development: 96/79). The rule-driven metrics therefore look mildly
optimistic on the development split (about 1-2 points). Limits of the audit: the 80% part was the
lexicon source during development, so it is not a blind test either; the audit bounds, but
cannot exclude, contamination. Paper: App. B caption and Limitations.

**B5. Per-example exports.** results/export/per_example/<backend>/<set>.csv.gz (32 files):
id, src_id, label, p_orig, p_norm and yhat for every system and seed saved at lambda = 0;
manifest.json with sha256. Texts are not exported (licences); ids map to rows of
data/prepared/<set>.jsonl, rebuilt deterministically by src/data/prepare.py.
scripts/reproduce_stats.py recomputes the paired bootstrap and Holm correction from these files
alone (numpy + pandas, no project imports); for mE5 it reproduces results/statistics/.../main.json
exactly (maximum absolute difference 0.0 over 20 comparisons).

**B6. Documentation.** This file; docs/DEVIATIONS.md D4; docs/CHANGELOG_REVISION.md.

## C. Claims that changed

C1. *Withdrawn:* "routing preserves quality at 12-19% lower measured compute than always
normalizing". Corrected: a router that reads the first pass costs 1.43-1.88 passes at lambda = 0
(1.69-1.88 for mE5), whereas B0 costs 1.00 and B1 0.89-1.05; routing is never cheaper than the
better single view and saves compute only relative to the two-view ensemble (1.89-2.05).
C2. *Withdrawn:* the abstract's "its value is a 12-19% saving of measured compute"; replaced by
"it costs more than either single view".
C3. *Weakened:* novelty wording (A3).
C4. *Withdrawn:* "much of the oracle headroom is noise" and the reading of "excess headroom" as
recoverable benefit; replaced by the reference interpretation (A4).
C5. *Corrected number:* few-label change vs zero-shot, -1.4 to +1.5 (mean -0.01).
C6. *Relabelled:* intrinsic normalizer scores are development results.
C7. *Relabelled:* reported costs are token-model *estimates* of measured latency, not end-to-end
measurements (previously "measured cost"); the end-to-end check agrees within 0.07 passes.
Unchanged: all accuracy results, all significance decisions, the framing decision (no consistent,
significant improvement over competitive baselines), the mechanism point estimates.

## E. Threats to validity that remain

1. Single task (binary sentiment) and frozen encoders with linear heads; fine-tuned or
   instruction-tuned models may behave differently.
2. No independent transliteration test set; the normalizer's intrinsic quality rests on
   development data (bounded by the audit, not excluded).
3. Cross-corpus differences confound dialect with platform, topic, period and label balance.
4. Costs per sentence are token-model estimates on one 4-core CPU; the end-to-end measurement
   covers 200 sentences per set, one router seed and lambda = 0; GPU or batched serving would change relative costs.
5. Mechanism intervals do not include estimator refitting variance; the target-CV ceiling uses
   linear models on the same features, so a richer model class could find more signal.
6. The noise reference depends strongly on how the reference classifiers are made; it cannot
   apportion the oracle headroom.
7. The pipeline was first exercised with a character n-gram classifier whose test results were
   inspected; this motivated the few-label setting (stated in Limitations).
8. Licences: TUNIZI, NArabizi and MYC state none and MARBERTv2 has none on its model card.
9. The +syn regime was added after the protocol (logged before it was run) and is exploratory.
