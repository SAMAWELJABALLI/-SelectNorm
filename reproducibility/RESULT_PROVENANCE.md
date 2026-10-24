# Result provenance

Each manuscript claim is traced along this chain:

**claim → table or figure → archived numbers → per-example predictions → run configuration → code → data and model**

The machine-readable version is [`result_provenance.json`](result_provenance.json). The check identifiers (C1–C9) refer to `scripts/verify_results.py`, whose last output is `verification_results.json`.

| # | R3 claim (section) | Table / figure | Archived numbers | Per-example evidence | Run (tag, script) | Check | Status |
|---|---|---|---|---|---|---|---|
| 1 | Macro-F1 of every system, encoder and set at λ = 0 (6.1) | Table 2 (`paper/tables/main.tex`) | `results/metrics/<enc>/runs_main.jsonl` | `results/export/per_example/<enc>/<set>.csv.gz`; `results/predictions/<enc>/routes/` | `main`; `experiments/run_all.sh`, `rerun_cost_fix.sh` | C2 (2,240 seed-level F1 from exports = logs), C3 (352 cells) | RECOMPUTED_FROM_ARCHIVE |
| 2 | Normalising gains 2–19 points on Tunisian/Algerian sets; sign on MYC depends on the encoder (abstract, 6.1) | Table 2 | as 1 | as 1 | `main` | B1−B0 from logs: 2.3 to 18.6 on $S_3$–$S_5$; MYC −8.0 to +8.7 | RECOMPUTED_FROM_ARCHIVE |
| 3 | SelectNorm-adapt vs B4: every paired 95% interval within ±0.7; Holm markers in Table 2 (6.1) | Table 2 markers; dossier Table S1 (`paired.tex`) | `results/statistics/<enc>/main.json` | exports | `experiments/run_stats.sh` | C4 (400 values re-derived by `reproduce_stats.py` from exports, exact); C6 | RECOMPUTED_FROM_ARCHIVE |
| 4 | Routers cost more than either single view; savings only relative to two passes (6.2) | Fig. 2 (`paper/figures/figure2_lisible/`) | `paper/figures/pareto.csv` ← `runs_main.jsonl` (`rel_cost`) | `results/predictions/*/probs.npz` (`__sec` timings) | `main` | C5 (324 values) | RECOMPUTED_FROM_ARCHIVE |
| 5 | Measured timings (6.2) | text | `results/metrics/measured_cost_reported.json` (mE5 from the re-timing, others from `measured_cost.json`) | `results/metrics/measured_cost_live/`, `measured_cost_mE5_retime_live/` | `src/evaluation/measured_cost.py` | not re-timed; 0 routing mismatches recorded in the files | AVAILABLE_NOT_EXECUTED |
| 6 | Disagreement AUC 0.62–0.74; source ρ̂ AUC ≤ 0.71, two below 0.5; target-trained reference 0.53–0.68 (6.3, M1–M2) | Table 3 (`mechanism.tex`), Fig. 3, dossier Table S4 | `results/statistics/<enc>/mechanism_cons.json` | needs `features/` (not distributed) | `experiments/run_all_mech.sh`, `revision_analyses.sh` | C6 (table regenerated from JSON = paper); Fig. 3 data = JSON (144 values, `paper/figures/figure3_horizontale/build_figure3_data.py`); AUCs themselves not recomputed | VERIFIED (table ↔ JSON); AUC computation AVAILABLE_NOT_EXECUTED |
| 7 | Benefit and headroom, noise reference (M3–M4) | Table 3; dossier Table S5 | `mechanism_cons.json`, `results/statistics/noise_sensitivity.json` | needs features | as 6 | C6 | VERIFIED (table ↔ JSON) |
| 8 | Ablations: safeguards −4.2 to −10.6; routing components ≤ 0.7 (6.4) | dossier Table S7 (`ablation.tex`), text | `runs_abl_*.jsonl`, `runs_main.jsonl` | `results/predictions/<enc>/routes/abl_*` | `experiments/run_all.sh` | C6 (regenerated table = paper) | RECOMPUTED_FROM_ARCHIVE |
| 9 | Few labels: −1.4 to +1.5 vs zero-shot, mean −0.01; targeted ≈ random (6.4) | text; dossier few-label figure (`paper/figures/fewlabel.csv`) | `runs_adapt.jsonl` (8 backends) | `results/audit/` (sampled indices) | `adapt`; `adapt_audit` | C7 (200 values); range recomputed: −1.40 to +1.49, mean −0.007; audit 0 violations; logged samples respect cross-fitting (test) | RECOMPUTED_FROM_ARCHIVE |
| 10 | RQ4: agreement with human transliteration 73–77% (6.4) | text | computed by `src/evaluation/tables.py` (`consistency`) from `probs.npz` and routes | needs `data/prepared` (NArabizi gold) | `main` | not regenerated without data | AVAILABLE_NOT_EXECUTED |
| 11 | +syn regime results (6.4) | dossier Table S2 (`main_syn.tex`) | `results/metrics/<enc>+syn/runs_main.jsonl` | exports `+syn` | `main` | C2, C3 | RECOMPUTED_FROM_ARCHIVE |
| 12 | Normaliser accuracy (development results) | dossier Table S8 (`intrinsic.tex`) | `results/metrics/intrinsic.json`, `tarc_audit.json` | needs TArC/NArabizi text | `src/normalization/intrinsic_eval.py` | C8 (15 cells) | VERIFIED (table ↔ JSON) |
| 13 | Linguistic conditions (taxonomy) (6.3) | dossier Table S6 (`taxonomy.tex`) | `results/statistics/<enc>/taxonomy.csv` | needs text | `src/evaluation/taxonomy.py` | C6 | VERIFIED (table ↔ CSV) |
| 14 | Qualitative examples (6.5) | Table 4 (`qualitative.tex`) | `results/qualitative/examples_mE5.json` (text masked) | `docs/aciids2027/EXAMPLE_PROVENANCE.md` | — | posteriors and routing per seed in JSON | VERIFIED (numbers ↔ JSON, by hand during R1) |

## Superseded or historical outputs (kept, not used for R3)

| Path | What it is | Replaced by |
|---|---|---|
| `results/archive/pre_cost_fix/` | `main` logs before the cost-accounting correction (D4) | `results/metrics/*/runs_main.jsonl`; λ = 0 identical (C9) |
| `results/archive/mE5_encodetime_costs/` | mE5 metrics with encoding-time costs | batch-size-1 latency costs (D2) |
| `results/archive/measured_cost_surrogate_head.json` | first end-to-end timing with a surrogate head | `measured_cost.json` (D5) |
| `results/archive/measured_cost_short_warmup.json` | timing with too short a warm-up, discarded | `measured_cost.json` |
| `results/archive/fewlabel_audit_v1.json` | first few-label audit | `results/statistics/fewlabel_audit.json` (D5) |
| `results/metrics/measured_cost.json` (mE5 rows) | first mE5 timing, overlapped a concurrent job | `measured_cost_mE5_retime.json` (reported) |
| `charlr` backends | development reference, test results inspected | not reported |
| `archive/prior_revisions/` | earlier manuscripts | `paper/` (R3) |
