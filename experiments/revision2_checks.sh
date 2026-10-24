#!/bin/bash
# Second revision: checks run after the end-to-end timing (no concurrent load during timing).
set -e
cd "$(dirname "$0")/.."
B=enc:intfloat/multilingual-e5-base
python3 -m src.routing.adapt --backend $B --tag adapt_audit --log-samples results/audit/fewlabel_samples_logged_enc_intfloat__multilingual-e5-base.jsonl
python3 -m src.evaluation.check_fewlabel --logged enc_intfloat__multilingual-e5-base=results/audit/fewlabel_samples_logged_enc_intfloat__multilingual-e5-base.jsonl
mkdir -p results/statistics/reproduced
for e in enc_intfloat__multilingual-e5-base enc_FacebookAI__xlm-roberta-base enc_sentence-transformers__LaBSE enc_UBC-NLP__MARBERTv2; do
  python3 -I scripts/reproduce_stats.py results/export/per_example $e > results/statistics/reproduced/$e.json
done
python3 -m src.evaluation.cost_threshold
echo ALL_DONE
