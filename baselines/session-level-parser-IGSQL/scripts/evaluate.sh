PYTHONIOENCODING='utf-8'
export PYTHONIOENCODING

LOGDIR="log"

cd data/SeSQL && python create_gold.py
cd ../..

python run/postprocess_eval.py --dataset=SeSQL --split=test --pred_file $LOGDIR/valid-eval_predictions.json --remove_from
