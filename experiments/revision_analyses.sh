#!/bin/sh
# Revision R4/R6: mechanism intervals (1,000 seed-averaged bootstrap resamples) and noise-reference sensitivity.
set -e
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  python3 -m src.evaluation.mechanism --backend "enc:$m" --noise --ci 1000
done
python3 -m src.evaluation.noise_sensitivity
