# Experiment matrix

The machine-readable matrix is [`experiment_matrix.csv`](experiment_matrix.csv): one row per run tag and backend (58 rows). `scripts/build_experiment_matrix.py` generates it from the archived run logs, so the configuration columns are read from what was run rather than typed by hand.

The matrix has these columns:
- experiment id;
- research question;
- encoder and pinned revision;
- classifier regime;
- normaliser;
- feature groups;
- estimator;
- seeds;
- λ grid;
- test sets;
- number of logged runs;
- script;
- hardware;
- output path and its SHA-256;
- manuscript element;
- status.

## Common settings

| Item | Value | Where |
|---|---|---|
| Classifier | logistic regression on frozen mean-pooled embeddings, C and temperature on `clf_dev_ar` | `src/models/classifier.py`, `results/predictions/*/classifier.json` |
| Regimes | Arabic-script only (primary); `+syn` = Arabic script + synthetic Latin renderings (exploratory, D1) | `docs/DEVIATIONS.md` |
| Policy split | `policy_pool`, 80% training and 20% threshold selection, permutation `default_rng(1000 + seed)` | `src/routing/run.py` |
| Seeds | 0–4 (encoders); 0–1 for some development runs of `charlr` | logs |
| λ grid | 0, 0.01, 0.02, 0.05, 0.1, 0.2 (`main` only; other tags λ = 0) | `src/routing/run.py` |
| Target adaptation of π̂ | two-fold cross-fitting by source id (`fold_of`) | `src/routing/run.py`, `adapt.py` |
| Few-label budgets | k ∈ {8, 16, 32, 64, 128}, 5 draws × 5 seeds | `src/routing/adapt.py` |
| Bootstrap | 10,000 resamples of test sentences, seed 12345, Holm over 5 comparisons × 4 sets per backend | `src/evaluation/stats.py`, `scripts/reproduce_stats.py` |
| Mechanism intervals | 1,000 seed-averaged bootstrap resamples, estimators not refitted | `src/evaluation/mechanism.py` |
| Hardware | 4-core x86_64 CPU, 4 threads, no GPU | `reproducibility/ENVIRONMENT.md` |

## Execution order of the archived runs

Taken from `results/logs/` and `docs/DEVIATIONS.md`:

1. `src/data/prepare.py`, then the views (`src/routing/views.py`) and the encoders (`src/models/encode.py`, `scripts`: `experiments/encode_extra.sh`).
2. `experiments/run_all.sh`: heads, latency, `main`, `adapt`, ablations. A container restart occurred after MARBERTv2 `abl_no_trel`; the three runs not yet started were then run with identical commands (D3, `results/logs/run_all_resume.log`).
3. `experiments/run_all_mech.sh` (mechanisms) and `experiments/run_stats.sh` (paired tests).
4. `experiments/rerun_cost_fix.sh`: `main` re-run after the cost-accounting correction (D4). The pre-fix logs are in `results/archive/pre_cost_fix/`; all λ = 0 rows are unchanged (check C9).
5. `experiments/revision_analyses.sh`: mechanism intervals and noise sensitivity.
6. `experiments/revision2_checks.sh`: few-label audit replay, stand-alone statistics, cost threshold. End-to-end timing: `src/evaluation/measured_cost.py`.

## Status values

| Status | Meaning |
|---|---|
| `current` | reported in R3 or in its technical dossier |
| `development` | `charlr` reference, whose test results were inspected during development (`docs/PROTOCOL.md`); not reported |

Superseded outputs are listed in `RESULT_PROVENANCE.md` and kept under `results/archive/`.
