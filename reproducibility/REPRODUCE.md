# Reproduction

Each level states what it actually does. Levels 1 and 2 **recompute** the reported numbers from archived predictions and logs; they do not re-run any experiment. Only level 3 re-executes the pipeline.

## Level 1: quick verification (no download, under a minute)

```bash
pip install -r requirements.txt
python3 -m pytest -q                       # 39 tests on synthetic fixtures and the archive
python3 scripts/verify_repository.py --check
python3 scripts/verify_results.py --quick  # C1-C3, C5-C9 (about 5 s)
```

## Level 2: statistical reproduction from the archive (about 4 minutes, 4 CPU cores)

```bash
python3 scripts/verify_results.py          # adds C4: 10,000-resample paired bootstrap for 4 encoders
python3 scripts/reproduce_stats.py results/export/per_example enc_intfloat__multilingual-e5-base --n 10000
python3 -m src.evaluation.tables --backends enc_intfloat__multilingual-e5-base,enc_FacebookAI__xlm-roberta-base,enc_sentence-transformers__LaBSE,enc_UBC-NLP__MARBERTv2 \
        --main enc_intfloat__multilingual-e5-base --out /tmp/tables   # stops at the RQ4 consistency table without data/prepared
python3 paper/figures/figure2_lisible/redraw_figure2_lncs.py
python3 paper/figures/figure3_horizontale/build_figure3_data.py && python3 paper/figures/figure3_horizontale/redraw_figure3_lncs.py
sh scripts/build_paper.sh                  # pdfLaTeX + BibTeX; 15 pages
```

`scripts/reproduce_stats.py` uses only the per-example exports. It does not import the project, so it is independent of the code that produced the archived statistics.

## Level 3: full re-execution (corpora and encoders required)

```bash
pip install -r requirements-gpu.txt
sh scripts/fetch_data.sh                   # clones the corpora at the paper's commits and checks digests
python3 -m src.data.prepare                # data/prepared/*.jsonl and prep_report.json (compare with the archived report)
python3 -c "from src.routing.views import build_views, SETS; [build_views(s) for s in SETS]"
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  python3 -m src.models.encode --model $m --views orig,cons,lex,rule
done
sh experiments/encode_extra.sh             # +syn and T_cov views
sh experiments/run_all.sh                  # heads, latency, main, adapt, ablations
sh experiments/run_all_mech.sh && sh experiments/run_stats.sh
sh experiments/revision_analyses.sh && sh experiments/revision2_checks.sh
python3 -m src.evaluation.measured_cost --model intfloat/multilingual-e5-base   # end-to-end timing (one encoder)
```

Outputs overwrite `results/` and `paper/tables/`. Compare them with the archived versions using `git diff` and `scripts/verify_results.py`.

Notes:

- The tuned thresholds and costs depend on measured per-sentence timings, so λ > 0 operating points will differ on other hardware. λ = 0 decisions do not depend on cost.
- Embeddings computed on other hardware may differ in the last digits; see `ENVIRONMENT.md`.
- Level 3 has not been executed from this repository (`VERIFICATION_REPORT.md`).

## GPU / Colab

`notebooks/colab_encode.ipynb` encodes the prepared views with `src.models.encode` on a Colab GPU.

- **Input:** a zip of the repository with `data/views/`.
- **Output:** `features.zip` holding `features/<model>/<set>__<view>.npy` and `__sec.npy` timing files, plus `features/HARDWARE.txt`.

Unzip the output at the repository root before running `experiments/run_all.sh`. Timing measured on a GPU is not comparable with the CPU costs reported in the paper.
