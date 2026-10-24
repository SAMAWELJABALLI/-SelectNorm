# Datasets and artefact redistribution

No corpus text is distributed in this repository. Public availability of a corpus does not give permission to redistribute it, and several of the corpora used here state no licence. Each corpus must be obtained from its authors. `scripts/fetch_data.sh` clones every upstream repository at the commit used in the paper. It then checks the SHA-256 of every file the pipeline reads against `data/raw_manifest.json`. After that, `python3 -m src.data.prepare` rebuilds `data/prepared/` deterministically (seed 13).

## Upstream corpora

| Corpus | Use | Upstream (commit) | Licence stated upstream | Redistributed here |
|---|---|---|---|---|
| TSAC (Medhaffar et al., 2017) | classifier training (Arabic script); policy pool and $S_3$ (Latin script) | github.com/fbougares/TSAC (`3995e70`) | LGPL-3.0 (`LICENSE` file) | no text; derived labels and predictions |
| TUNIZI (Fourati et al.) | $S_4$ test | github.com/chaymafourati/TUNIZI-Sentiment-Analysis-Tunisian-Arabizi-Dataset (`33a341c`) | none found | no text; derived labels and predictions |
| NArabizi (Seddah et al., 2020; Touileb & Barnes, 2021) | $S_5$ test, human transliterations (RQ4) | github.com/SamiaTouileb/Narabizi (`1434f57`) | UD treebank CC BY-SA 4.0; sentiment layer: none found | no text; derived labels and predictions |
| MYC (Moroccan YouTube Corpus) | $S_6$ test | github.com/MouadJb/MYC (`645d51a`) | none found | no text; derived labels and predictions |
| TArC (Gugliotta & Dinarelli) | normaliser lexicon (80% split), normaliser development | github.com/eligugliotta/tarc (`ee2b293`) | README: "Attribution 4.0 International (CC BY-NC-SA 4.0)" (the heading is internally inconsistent; read as CC BY-NC-SA 4.0) | indices of the sentences used (`data/prepared/tarc_train_ids.json`) |

Full commit hashes and file digests: `data/raw_manifest.json`. Sentence counts after de-duplication and near-copy removal: `data/prepared/prep_report.json` and Table 1 of the paper.

## Artefact redistribution matrix

| Artefact | Contains corpus text? | In repository | Reason |
|---|---|---|---|
| `data/raw/`, `data/prepared/*.jsonl`, `data/views/` | yes | **no** | corpora without a redistribution licence (TUNIZI, MYC, NArabizi sentiment layer) |
| `features/` (encoder embeddings, 1.1 GB) | no, but invertible information about the text | **no** | size; derived from restricted text; regenerable |
| model weights | no | **no** | obtained from the Hugging Face Hub at pinned revisions (`reproducibility/MODELS.md`) |
| `results/predictions/*/probs.npz`, `routes/` | no (posteriors and decisions per row index) | yes | needed to recompute tables; contains no text |
| `results/export/per_example/*.csv.gz` | no (row index, source-id hash, gold label, posteriors, predictions) | yes | needed for independent statistical tests |
| `results/statistics/*/examples.jsonl` | text **removed** in this repository | yes, masked | original files held raw sentences from all four test sets; replaced by row index, source id and SHA-256 of the text |
| `results/qualitative/examples_mE5.json` | text **removed** | yes, masked | as above (included MYC sentences) |
| `results/qualitative/private/` | yes | **no** | MYC sentence texts, kept privately |
| `paper/tables/qualitative.tex` (Table 4) | TSAC and NArabizi sentences only; MYC rows withheld | yes | TSAC under LGPL-3.0 and NArabizi (UD) under CC BY-SA 4.0, with attribution in the paper; licence conditions are the authors' responsibility to confirm before publication |
| `results/audit/` | no (indices and source-id hashes) | yes | audit of few-label sampling |
| gold labels per row (inside exports) | no text | yes | derived annotation; **flag for the authors**: confirm that releasing per-row labels of TUNIZI and MYC is acceptable before making the repository public |

The source identifiers (`src_id`) are the first 12 hex digits of an MD5 of the corpus name and the original position (`src/data/prepare.py`, `sid`). They allow rows to be matched once the corpora are obtained independently.

## What a user must supply

1. The five upstream repositories at the listed commits (`scripts/fetch_data.sh`).
2. For full re-execution, the encoder weights from the Hugging Face Hub (downloaded automatically by `src/models/encode.py` at the pinned revisions).
