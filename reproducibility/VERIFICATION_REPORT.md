# Verification report

**Date:** 2026-10-24.

**Scope:** this repository at the commit that adds this file.

**Clean-environment run:**
- fresh `git clone` of the repository;
- new Python 3.13 virtual environment;
- `pip install -r requirements.txt`;
- the commands below.

Machine-readable output of the numerical checks: `verification_results.json`.

## Status vocabulary

| Status | Meaning |
|---|---|
| `VERIFIED` | an output was compared with an independent source and agreed within the stated tolerance |
| `RECOMPUTED_FROM_ARCHIVE` | the reported numbers were recomputed from archived predictions or logs and agree; the experiment itself was not re-run |
| `EXECUTED_SUCCESSFULLY` | the step was run here and produced the expected output |
| `AVAILABLE_NOT_EXECUTED` | code and instructions are present; not run here |
| `BLOCKED` | could not be run (reason given) |
| `FAILED` | was run and disagreed |

## Components

| Component | Present | Tested | Reproduced | Status | Limitation |
|---|---|---|---|---|---|
| Manuscript source integrity | `paper/` = supplied R3 LaTeX zip (`diff -r`) | yes | — | VERIFIED | — |
| PDF compilation | `scripts/build_paper.sh` | yes (clean clone) | 15 pages; text identical to the supplied PDF; all 15 pages pixel-identical at 72 dpi; no undefined reference or citation, no missing character | VERIFIED | the CI paper build uses Ubuntu TeX Live packages and has not run yet |
| Dataset preparation | `scripts/fetch_data.sh`, `src/data/prepare.py`, `data/raw_manifest.json` | yes (clean clone, upstream clones at pinned commits) | all 15 raw-file digests match; the 10 `data/prepared/*.jsonl` and `prep_report.json` are byte-identical to the archived preparation | EXECUTED_SUCCESSFULLY, VERIFIED | depends on the upstream repositories staying online |
| Pretrained encoder loading | `src/models/encode.py`, pinned revisions | no | — | AVAILABLE_NOT_EXECUTED | needs the model downloads (about 2 GB) |
| Frozen representation extraction | `src/models/encode.py`, `notebooks/colab_encode.ipynb` | no | — | AVAILABLE_NOT_EXECUTED | `features/` (1.1 GB) is not distributed |
| Logistic classification heads | `src/models/classifier.py`; selected C and temperature in `results/predictions/*/classifier.json` | no | — | AVAILABLE_NOT_EXECUTED | needs features |
| Normalisation | `src/normalization/arabizi.py` | 15 unit tests (determinism, lexicon, negation, laughter, French/English protection, `T_cov`, orthography) | — | EXECUTED_SUCCESSFULLY | intrinsic accuracy only checked as table ↔ JSON (C8); recomputing it needs TArC and NArabizi text |
| Routing | `src/routing/` | unit tests (factorisation identity, sign recovery, thresholds, branch selection, sunk/avoidable cost, folds, empty disagreement set) | λ = 0 decisions re-derived from exports (C2) | EXECUTED_SUCCESSFULLY, RECOMPUTED_FROM_ARCHIVE | routers not re-fitted (needs features) |
| Baselines (B0–B6, R) | `src/routing/run.py` | via C2/C3 | Table 2: 352 cells = logs; 2,240 seed-level macro-F1 recomputed from per-example predictions = logs (|d| ≤ 1e-6) | RECOMPUTED_FROM_ARCHIVE | — |
| Ablations | `runs_abl_*.jsonl` | C6 | regenerated `ablation.tex` = paper | RECOMPUTED_FROM_ARCHIVE | — |
| Statistical tests | `scripts/reproduce_stats.py` (independent of the project code), `src/evaluation/stats.py` | C4, unit tests (macro-F1 = sklearn, resampling = row duplication, Holm) | 400 values (diff, CI, p, Holm p; 4 encoders × 20 comparisons) identical (|d| ≤ 1e-9) | VERIFIED | — |
| Mechanism diagnostics (AUC, headroom) | `results/statistics/*/mechanism_cons.json` | C6; Fig. 3 data builder | Table 3 and the interval table regenerated = paper; Fig. 3 data = JSON (144 values) | RECOMPUTED_FROM_ARCHIVE (tables); AVAILABLE_NOT_EXECUTED (AUC computation) | AUCs need features |
| Figures | Fig. 1 TikZ; Figs. 2–3 scripts and CSV; few-label figure | C5, C7; scripts run in the clean clone | Fig. 2 data (324 values) and few-label data (200 values) = logs; regenerated Figs. 2–3 pixel-identical (PDF bytes differ only in metadata) | RECOMPUTED_FROM_ARCHIVE | — |
| Few-label audits | `results/audit/`, `results/statistics/fewlabel_audit.json` | unit test on logged samples; C7 | logged labels always come from the other fold and targeted labels are disagreements (re-checked from exports); archived audit: 0 violations | VERIFIED | replay script needs data |
| Timing measurements | `results/metrics/measured_cost*.json`, `latency_*.json` | no | — | AVAILABLE_NOT_EXECUTED | hardware-dependent; not re-timed |
| Cost-accounting correction (D4) | `results/archive/pre_cost_fix/` | C9 | all 5,280 λ = 0 rows unchanged (macro-F1 and selection rate) | VERIFIED | — |
| RQ4 consistency (73–77%) | `src/evaluation/tables.py` | no | — | AVAILABLE_NOT_EXECUTED | needs `data/prepared` (reproducible after `fetch_data.sh`) |
| Repository integrity | `scripts/verify_repository.py`, `file_manifest.json` | yes (clean clone) | 13,547 files match; no restricted artefact; no credential pattern | VERIFIED | — |
| Full experiment re-execution | `experiments/*.sh` | no | — | AVAILABLE_NOT_EXECUTED | not attempted |

## Commands executed in the clean clone

```text
pip install -r requirements.txt            -> numpy 2.5.3, pandas 3.0.5, scikit-learn 1.9.1, scipy 1.18.1, matplotlib 3.11.2, wordfreq 3.1.1, pytest 9.1.1
python -m pytest -q                        -> 39 passed
python scripts/verify_repository.py --check -> OK: 13547 files match the manifest
python scripts/verify_results.py           -> C1-C9 PASS (14,133 comparisons, 0 failures; 3 min 21 s)
sh scripts/build_paper.sh                  -> 15 pages; text identical to the supplied R3 PDF
python paper/figures/.../redraw_*.py       -> Figs. 2-3 regenerated, pixel-identical
sh scripts/fetch_data.sh                   -> 15/15 raw-file digests OK
python -m src.data.prepare                 -> 10/10 prepared files and prep_report.json byte-identical
```

## Tolerances

| Check | Tolerance | Reason |
|---|---|---|
| C2 | 1e-6 macro-F1 points | float summation order (sklearn vs NumPy) |
| C4, C5, C7, C9 | 1e-9 | same arithmetic, same seed |
| C3, C6, C8 | exact string equality after rounding as printed | the tables are rounded |

## Not established

- No experiment was re-run (encoding, heads, routers, timing).
- Nothing was run on a second machine.
- The CI workflows have not run yet: the remote repository did not exist when this report was written.

See `DISCREPANCIES.md` for the full register.
