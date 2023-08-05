# SeSQL_EX-RATSQL

## Setup

Follow the instructions in [DuoRAT](https://github.com/ElementAI/duorat).

## Running the code

Preprocess the data:
```
python data/convert.py
```

Train the model:
```
python -u scripts/train.py --config configs/duorat/duorat-finetune-bert-base.jsonnet --logdir ./logdir/duorat-bert-base
```
Training will further save a number of files in the (mounted) log directory `./logdir/duorat-bert-base`: the config that was used `config-{date}.json`, model checkpoints `model_{best/last}_checkpoint`, some logs `log.txt`, and the inference outputs `output-{step}`.
During training, inference is run on the dev set once in a while.
Here's how you can run inference manually:
```
python scripts/infer.py --logdir ./logdir/duorat-bert-base --output ./logdir/duorat-bert-base/my_inference_output
python scripts/eval.py --config configs/duorat/duorat-good-no-bert.jsonnet --section val --inferred ./logdir/duorat-bert-base/my_inference_output --output ./logdir/duorat-bert-base/my_inference_output.eval
```