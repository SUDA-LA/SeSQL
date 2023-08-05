#export PYTHONPATH=./
#export CACHE_DIR=./logdir
#export TRANSFORMERS_CACHE=./logdir
#export CORENLP_HOME=./third_party/corenlp/stanford-corenlp-full-2018-10-05
export CUDA_VISIBLE_DEVICES=1,2
#nohup python -u scripts/train.py --config configs/duorat/duorat-finetune-bert-base.jsonnet --logdir ./logdir/duorat-sesql-single-round-bert-base-max-step-100000 > ./log/duorat_sesql_single_round_bert_base_max_step_100000.log 2>&1 &
#python -u scripts/train.py --config configs/duorat/duorat-finetune-bert-base.jsonnet --logdir ./logdir/duorat-sesql-bert-wwm-test --seed 512
python -u scripts/train.py --config configs/duorat/duorat-finetune-bert-base.jsonnet --logdir ./logdir/duorat-sesql-single-round-bert-base-max-step-100000