PYTHONIOENCODING='utf-8'
export PYTHONIOENCODING

LOGDIR="logs_SeSQL_editsql"
python3 postprocess_eval.py --dataset=SeSQL --split=dev --pred_file $LOGDIR/valid_use_predicted_queries_predictions.json --remove_from
