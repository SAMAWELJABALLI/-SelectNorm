# Models

All encoders are used **frozen** (no fine-tuning). Sentence embeddings are mean-pooled over the last layer, with maximum length 128 and batch size 32 (`experiments/configs/encoders.json`). `src/models/encode.py` loads each model at the revision pinned in `experiments/configs/encoder_revisions.json`. The SHA-256 digests in that file were recorded from the downloaded weights; the loader does not re-check them.

| Short name | Hugging Face identifier | Revision | Weights file | SHA-256 (weights) | Licence (model card) |
|---|---|---|---|---|---|
| XLM-R | `FacebookAI/xlm-roberta-base` | `e73636d4f797dec63c3081bb6ed5c7b0bb3f2089` | model.safetensors | `6fd4797b…` | MIT |
| mE5 | `intfloat/multilingual-e5-base` | `d128750597153bb5987e10b1c3493a34e5a4502a` | model.safetensors | `a18a44fa…` | MIT |
| LaBSE | `sentence-transformers/LaBSE` | `836121a0533e5664b21c7aacc5d22951f2b8b25b` | model.safetensors | `77d8e1f2…` | Apache-2.0 |
| MARBERTv2 | `UBC-NLP/MARBERTv2` | `fe88db9db8ccdb0c4e1627495f405c44a5f89066` | pytorch_model.bin | `5d34aca0…` | **none stated** |

Full digests are in `experiments/configs/encoder_revisions.json`. mE5 inputs carry the `query: ` prefix. No model weights are stored in this repository. MARBERTv2 states no licence; it is used for research only and is not redistributed.

**Classifier heads.** Logistic regression on the frozen embeddings, with C chosen on `clf_dev_ar` and temperature scaling (`src/models/classifier.py`; selected values in `results/predictions/<backend>/classifier.json`).

**Routers.**
- Logistic regression on standardised decision features (`src/routing/policies.py`).
- Ablation: histogram gradient boosting (`abl_gbm`).
- The development reference `charlr` (character n-gram logistic regression) is not an encoder and is not reported.
