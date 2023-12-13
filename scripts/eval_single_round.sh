# !/bin/bash

gold=data/example/single_round_examples.json     # file/to/gold
pred=data/example/single_round_predict_examples.json     # file/to/pred
db=data/SeSQL/db_content.json # dir/to/database
table=data/SeSQL/tables.json  # file/to/table

python scripts/evaluation_single_round.py --gold $gold --pred $pred --db $db --table $table --etype match
