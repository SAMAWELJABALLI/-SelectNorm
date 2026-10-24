#!/bin/sh
# Full SelectNorm pipeline after features/ exist (CPU; encoders are frozen, nothing is fine-tuned).
set -e
ENCODERS="${ENCODERS:-intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2}"
SEEDS=0,1,2,3,4
for m in $ENCODERS; do
  python3 -m src.models.classifier --backend "enc:$m"
  python3 -m src.models.classifier --backend "enc:$m" --syn
  # batch-size-1 latency on the idle machine; rewrites the per-sentence costs of both regimes
  python3 -m src.evaluation.latency --model "$m"
done
for m in $ENCODERS; do
  for B in "enc:$m" "enc:$m+syn"; do
    python3 -m src.routing.run --backend "$B" --seeds $SEEDS --tag main
    python3 -m src.routing.adapt --backend "$B" --seeds $SEEDS --tag adapt
    python3 -m src.routing.run --backend "$B" --seeds $SEEDS --mode cov  --tag abl_cov
  done
  B="enc:$m"
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --mode lex  --tag abl_lex
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --mode rule --tag abl_rule
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --groups conf --tag abl_conf_only
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --groups script,trel --tag abl_no_conf
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --groups conf,script --tag abl_no_trel
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --groups conf,trel --tag abl_no_script
  python3 -m src.routing.run --backend "$B" --seeds $SEEDS --groups conf,script,trel,emb --tag abl_emb
done
python3 -m src.routing.run --backend "enc:intfloat/multilingual-e5-base" --seeds $SEEDS --est gbm --tag abl_gbm
