# Changelog

## R3 research release (repository creation)

Inherited material (first commit): code, configurations, run logs, statistics, predictions, per-example exports, audits and superseded runs from the working repository (history up to revision 3, local commit `72cfade`), the R3 manuscript sources and PDF, and prior revisions.

Changes made while building the repository, kept out of the manuscript:

- Corpus text removed or masked (see `reproducibility/DATASETS.md`): `data/raw`, `data/prepared/*.jsonl`, `data/views`, `features/` are not included; text fields in `results/statistics/*/examples.jsonl` and `results/qualitative/examples_mE5.json` replaced by row indices, source ids and SHA-256 digests.
- `src/routing/policies.py::fit_proba`: returns a constant 1/2 when it receives no training example (for instance no disagreement in a labelled split) instead of raising `ValueError`. No archived run met this case; `scripts/verify_results.py` reproduces every archived number after the change.
- Added: README, reproducibility documentation, `scripts/verify_results.py`, `scripts/verify_repository.py`, `scripts/fetch_data.sh`, `scripts/build_paper.sh`, `data/raw_manifest.json`, tests, CI workflows, environment files.
- `notebooks/colab_encode.ipynb` moved from `scripts/`; `results/logs/` moved from `logs/`.

## Manuscript history

See `docs/` and `archive/prior_revisions/`: full draft (ACL format), LNCS revision 1, revision 2, and R3 (`paper/`, with `docs/aciids2027/r3/JOURNAL_R3_FR.md`).
