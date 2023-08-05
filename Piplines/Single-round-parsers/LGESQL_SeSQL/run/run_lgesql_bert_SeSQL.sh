device=0
# CUDA_VISIBLE_DEVICES=$device nohup python scripts/text2sql.py > ./log/train_LGESQL_SeSQL_dataset_Bert_Base_Chinese_seed_100.log 2>&1 &
CUDA_VISIBLE_DEVICES=$device python scripts/text2sql.py