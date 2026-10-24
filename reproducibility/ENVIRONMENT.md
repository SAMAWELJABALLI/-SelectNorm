# Environment

## Environment of the archived runs

All archived runs, from data preparation to statistics, were produced in a single Linux container (x86_64, 4 CPU cores, no GPU) between 2026-10-22 and 2026-10-23.

Timing used `torch.set_num_threads(4)`, with batch size 1 for the latency model and the end-to-end timing. The CPU and torch version are recorded in `results/metrics/measured_cost.json` and `results/metrics/latency_*.json`.

Package versions are those installed in that container. The installation timestamps (2026-10-22, 19:24–19:35 UTC) precede the first encoder run (encode log, 20:41 UTC), and no package was upgraded afterwards:

| Package | Version |
|---|---|
| Python | 3.13.16 |
| numpy | 2.5.3 |
| pandas | 3.0.5 |
| scipy | 1.18.1 |
| scikit-learn | 1.9.1 |
| matplotlib | 3.11.2 |
| wordfreq | 3.1.1 (required by the $T_{\rm cons}$ safeguards) |
| torch | 2.14.1+cu130 (run on CPU) |
| transformers | 5.20.2 |
| tokenizers | 0.23.3 |
| safetensors | 0.8.0 |
| huggingface_hub | 2.2.0 |

sentence-transformers was **not** used: pooling is implemented in `src/models/encode.py`.

pytest 9.1.1 and ruff 0.16.9 were added when this repository was built, for tests only.

## Installation

| Purpose | File | Notes |
|---|---|---|
| Verification, statistics, tests (CPU) | `requirements.txt` | no download of models or corpora |
| Encoders and timing | `requirements-gpu.txt` | install the torch build that matches your CUDA driver for GPU use |
| Conda | `environment.yml` | Python 3.13 plus `requirements.txt` |

The Colab notebook (`notebooks/colab_encode.ipynb`) installs `transformers>=4.44` and `sentencepiece`, encodes the prepared views on a GPU and writes `features/HARDWARE.txt`. No such file exists for the archived features. The encode logs (`results/logs/encode*.log`) show that the archived features were computed in the container described above.

## Precision and determinism

- Linear heads and routers are deterministic given the seeds (policy split `default_rng(1000 + seed)`, estimator `random_state`).
- Bootstraps use `default_rng(12345)`.
- Encoder embeddings on a different device or BLAS may differ in the last floating-point digits. A full re-run should therefore reproduce macro-F1 to within rounding, not bit-for-bit. This has not been tested on another machine (`reproducibility/VERIFICATION_REPORT.md`).
