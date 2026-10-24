#!/bin/sh
# Paired bootstrap (10k) per backend. Family 1 = the protocol's main comparisons (Holm within it);
# family 2 = secondary comparisons (theory threshold, B4b, two-view ensemble), Holm within it.
MAIN=B5_selectnorm_adapt:B0_original,B5_selectnorm_adapt:B1_always,B5_selectnorm_adapt:B3_conf,B5_selectnorm_adapt:B4_direct_gain,B5_selectnorm_adapt:B5_selectnorm_src
SEC=B5_selectnorm_adapt_theory:B0_original,B5_selectnorm_adapt_theory:B1_always,B5_selectnorm_adapt_theory:B4_direct_gain,B5_selectnorm_adapt:B4b_abs_loss,B5_selectnorm_adapt:R_two_view_ensemble
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  for B in "enc:$m" "enc:$m+syn"; do
    python3 -m src.evaluation.stats --backend "$B" --tag main --pairs $MAIN --name main
    python3 -m src.evaluation.stats --backend "$B" --tag main --pairs $SEC --name main_secondary
  done
done
