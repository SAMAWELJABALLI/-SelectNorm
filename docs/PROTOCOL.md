# SelectNorm experimental protocol (fixed before the encoder runs)

Written 2026-10-22, before any frozen-encoder feature existed in this project. Everything
below applies unchanged to every encoder backend. Deviations will be listed in
`docs/DEVIATIONS.md` with their reason and date.

## What was already seen during development

The pipeline was developed with a sparse character n-gram classifier (`charlr`), which is
not an encoder and is reported only as a development reference. Its test-set numbers were
inspected during development. Two design decisions were made after that inspection and are
disclosed as such:
1. the diagnosis that, for `charlr`, the disagreement rate pi is stable across dialects
   while the conditional win rate rho shifts (TSAC-Latin 0.90 vs MYC 0.43);
2. consequently, the few-label adaptation setting (`src/routing/adapt.py`) was added.
The transliteration safeguards were tuned on the TArC held-out split (Tunisian), which acts
as the normalizer's development set; NArabizi gold is the untouched intrinsic check.

## Data roles

| Role | Set | Labels used for |
|---|---|---|
| Classifier training | `clf_train_ar` (Arabic-script TSAC, 90%) | fitting f |
| Classifier selection | `clf_dev_ar` (10%) | C, temperature |
| Policy training | `policy_pool` 80% per seed (human Latin-script TSAC, never seen by f) | pi (label-free), rho, baselines |
| Policy selection | `policy_pool` 20% per seed | thresholds of tuned policies |
| Test, in-corpus | `S3_tsac_lat` | final scoring only |
| Test, cross-corpus Tunisian | `S4_tunizi` | final scoring only |
| Test, Algerian | `S5_narabizi` (+ `S5ar_narabizi_gold`, same src_id) | final scoring; RQ4 pairs |
| Test, Moroccan | `S6_myc_lat` | final scoring only |
| Arabic-script controls | `S0_tsac_ar`, `S6ar_myc_ar` | f diagnostics (T is the identity) |

Exact duplicates are removed within sets, and test or policy sentences that are near-copies
(char 3-gram cosine >= 0.9) of classifier-training or policy sentences are removed
(`data/prepared/prep_report.json`).

## Systems

B0 original only; B1 always normalize (T_cons); B2 random routing at the selection rate of
B5-adapt (20 draws); B3 confidence threshold (tuned on policy-dev); B4 direct gain estimator
P(help|z) - P(harm|z) (post-hoc deferral style); B4b absolute per-view loss prediction
(learning-loss style); B4-lex learned routing with T_lex (no safeguards); B5 SelectNorm
(factorized estimator; `src` = source only, `adapt` = pi re-estimated on unlabeled target
text with two-fold cross-fitting; `theory` = Bayes threshold lambda * c instead of a tuned one);
B6 oracle (normalize iff normalization corrects an error; ties and joint errors keep the
original, no cost); R two-view ensemble (always both passes, accuracy reference).

Few-label setting (reported separately; it uses target labels): k in {8,16,32,64,128},
5 draws, two-fold cross-fitting; SN_targeted, SN_random, DG_random, CONF_random, SET_random.

## Primary analysis

* Primary metric: macro-F1 per test set; secondary: accuracy, selection rate, harmful
  transformations (normalization turns a correct prediction wrong) per 100 inputs and among
  routed inputs, share of oracle opportunities captured, relative measured cost.
* Main comparisons (per test set): B5-adapt vs B0, B1, B3, B4; B5-adapt vs B5-src.
* Five seeds (policy split + estimator seed). Uncertainty: paired bootstrap over source
  sentences, 10,000 resamples, statistic = difference in seed-averaged macro-F1; two-sided
  p-values with Holm correction over all main comparisons of one encoder.
* A difference is called practically relevant only if its 95% interval excludes zero and
  its point estimate is at least 1 macro-F1 point.
* lambda grid {0, .01, .02, .05, .1, .2} gives the operating points of the accuracy-cost
  figure; lambda = 0 is the main table.
* Features: groups conf, script, trel (default); emb (16-d PCA of the original-view
  embedding, fitted on policy-train) is an ablation.
* Estimator: logistic regression (main); gradient boosting (ablation).
