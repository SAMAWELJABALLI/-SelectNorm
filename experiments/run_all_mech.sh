#!/bin/sh
# Mechanism analysis (after experiments/run_all.sh)
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  python3 -m src.evaluation.mechanism --backend "enc:$m" --noise
  python3 -m src.evaluation.mechanism --backend "enc:$m" --groups conf,script,trel,emb
  python3 -m src.evaluation.mechanism --backend "enc:$m+syn"
  python3 -m src.evaluation.mechanism --backend "enc:$m" --mode cov
done
