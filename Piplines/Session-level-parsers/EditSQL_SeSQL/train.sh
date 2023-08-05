#! /bin/bash

PYTHONIOENCODING='utf-8'
export PYTHONIOENCODING

# export CUDA_VISIBLE_DEVICES=1
GLOVE_PATH="./path/to/data/glove.840B.300d.txt" # you need to change this
LOGDIR="logs_chase_editsql"

python3 run.py --raw_train_filename="data/chase_data_removefrom/train.pkl" \
          --raw_validation_filename="data/chase_data_removefrom/dev.pkl" \
          --database_schema_filename="data/chase_data_removefrom/tables.json" \
          --embedding_filename=$GLOVE_PATH \
          --data_directory="processed_data_chase_removefrom" \
          --input_key="utterance" \
          --state_positional_embeddings=1 \
          --discourse_level_lstm=1 \
          --use_utterance_attention=1 \
          --use_previous_query=1 \
          --use_query_attention=1 \
          --use_copy_switch=1 \
          --use_schema_encoder=1 \
          --use_schema_attention=1 \
          --use_encoder_attention=1 \
          --use_bert=1 \
          --bert_type_abb=cnS \
          --fine_tune_bert=1 \
          --use_schema_self_attention=1 \
          --use_schema_encoder_2=1 \
          --interaction_level=1 \
          --reweight_batch=1 \
          --freeze=1 \
          --train=1 \
          --logdir=$LOGDIR \
          --evaluate=1 \
          --evaluate_split="valid" \
          --use_predicted_queries=1
