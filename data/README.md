# Data

This folder ships no corpus text (see `reproducibility/DATASETS.md`).

| File | Content |
|---|---|
| `raw_manifest.json` | upstream URL, commit and SHA-256 of every raw file read by `src/data/prepare.py` |
| `prepared/prep_report.json` | set sizes, class counts and removals (duplicates, near-copies) of the archived preparation |
| `prepared/tarc_train_ids.json` | indices of the TArC sentences used to build the normaliser lexicon (80% split) |

To rebuild: `sh scripts/fetch_data.sh`, then `python3 -m src.data.prepare` (writes `prepared/*.jsonl`, which git ignores), then build the views (`src/routing/views.py`).
