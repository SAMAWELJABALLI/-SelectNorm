#!/bin/sh
for m in intfloat/multilingual-e5-base FacebookAI/xlm-roberta-base sentence-transformers/LaBSE UBC-NLP/MARBERTv2; do
  python3 -m src.models.encode --model $m --views gsyn --sets clf_train_ar,clf_dev_ar
  python3 -m src.models.encode --model $m --views cov --sets policy_pool,S3_tsac_lat,S4_tunizi,S5_narabizi,S6_myc_lat
done
