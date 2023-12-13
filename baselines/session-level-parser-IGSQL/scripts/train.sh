#! /bin/bash

PYTHONIOENCODING='utf-8'
export PYTHONIOENCODING

export CUDA_VISIBLE_DEVICES=6
GLOVE_PATH="" # our exp only use BERT.
LOGDIR="log"

python3 run.py --raw_train_filename="data/SeSQL_data_removefrom/train.pkl" \
          --raw_validation_filename="data/SeSQL_data_removefrom/dev.pkl" \
          --raw_test_filename="data/SeSQL_data_removefrom/test.pkl" \
          --database_schema_filename="data/SeSQL_data_removefrom/tables.json" \
          --embedding_filename=$GLOVE_PATH \
          --data_directory="processed_data_SeSQL_removefrom" \
          --input_key="utterance" \
          --state_positional_embeddings=1 \
          --discourse_level_lstm=1 \
          --use_schema_encoder=1 \
          --use_schema_attention=1 \
          --use_encoder_attention=1 \
          --use_bert=1 \
          --fine_tune_bert=1 \
          --bert_type_abb=cnS \
          --interaction_level=1 \
          --reweight_batch=1 \
          --train=1 \
          --use_previous_query=1 \
          --use_query_attention=1 \
          --logdir=$LOGDIR \
          --evaluate=1 \
          --evaluate_split="valid&test" \
          --use_utterance_attention=1 \
          --use_predicted_queries=1
