# Input manifest and audit

## Inputs

The repository was assembled from the working repository of the project (`SelectNorm/`, local git history `d791c1e` … `72cfade`). The supplied archives are snapshots of that working repository, and each was checked against the release file by file:

| Supplied input | SHA-256 | Relation to this repository |
|---|---|---|
| `SelectNorm_code.zip` (64 files) | `eab5500c…1f2839` | identical to `src/`, `experiments/`, `docs/` except: `src/evaluation/figures.py` (the archive predates the LNCS `--lncs` option, commit `c3c0aa0`); `src/routing/policies.py` (empty-set fix, see `CHANGELOG.md`); `scripts/encode_extra.sh` moved to `experiments/`; `scripts/colab_encode.ipynb` moved to `notebooks/`; bytecode caches dropped |
| `SelectNorm_results.tar.gz` | `72c1cd5c…be5313` | identical to `results/` except the five `results/statistics/*/examples.jsonl`, whose text fields were masked (`DATASETS.md`). The routed predictions (`results/predictions/`, 59 MB) are not in this archive; they come from the working repository |
| `per_example_predictions.tar.gz` | `e9939249…1faa8` | identical to `results/export/per_example/` and `scripts/reproduce_stats.py` |
| `SelectNorm_ACIIDS2027_R3_LaTeX.zip` | `d2eb0517…0e13b` | identical to `paper/` (`diff -r`), build outputs excluded |
| `SelectNorm_ACIIDS2027_R3.pdf` (15 pages) | `b721b660…aee595` | stored as `paper/compiled/SelectNorm_ACIIDS2027_R3.pdf`. A rebuild from `paper/` gives identical text and pixel-identical pages at 72 dpi |
| `SelectNorm_ACIIDS2027_R2_TechnicalDossier.pdf` | `776d05f4…af9d69c8` | the R2 build of the dossier. The R3 dossier source is `paper/supplement/supplement.tex`, which has the same tables; the R2 PDF is not used to override R3 |

**Source priority**, from most to least authoritative:
1. R3 manuscript and LaTeX (`paper/`);
2. code (`src/`, `experiments/`);
3. execution artefacts (`results/`);
4. the dossier;
5. earlier revisions (`archive/`).

No conflict between these sources was found for any reported number (`VERIFICATION_REPORT.md`). Documentation discrepancies are listed in `DISCREPANCIES.md`.

## File-level manifest

`file_manifest.json` lists every file of the repository with its SHA-256 and size. `python3 scripts/verify_repository.py --check` verifies it, and CI runs the check on every push. The check also fails if any of the following is present:
- corpus text under `data/`;
- encoder features or model weights;
- a credential pattern.

## Size

About 13,500 files, 65 MB. Most of this is the routed predictions (13,200 small `.npz` files under `results/predictions/*/routes/`). The largest single file is under 1 MB. No Git LFS is used.
