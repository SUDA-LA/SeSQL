# !/bin/bash
PYTHONIOENCODING='utf-8'
export PYTHONIOENCODING

gold=data/example/session_level_examples.json     # file/to/gold
pred=data/example/session_level_predict_examples.json     # file/to/pred
db=data/SeSQL/db_content.json                      # dir/to/database
table=data/SeSQL/tables.json                       # file/to/table

python scripts/session_preprocess.py --in_file $gold --out_file gold.txt
python scripts/session_preprocess.py --in_file $pred --out_file pred.txt

python scripts/eval_scripts/evaluation_sqa.py --db $db --table $table --etype match --gold gold.txt --pred pred.txt
