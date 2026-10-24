#!/bin/sh
# Revision R1: corrected cost model (sunk f(x)+T(x) vs avoidable f(T(x))). Only the main tag
# reports costs and lambda > 0 operating points, so only it is re-run; lambda = 0 is unaffected.
set -e
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  for B in "enc:$m" "enc:$m+syn"; do
    python3 -m src.routing.run --backend "$B" --seeds 0,1,2,3,4 --tag main
  done
done
