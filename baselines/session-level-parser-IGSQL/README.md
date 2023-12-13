# IGSQL

Our code is mainly adapted in the released [IGSQL](https://github.com/headacheboy/IGSQL).
Our main change is to adapt Chinese, for other details, please refer to the original IGSQL.

### Dependency

The model is tested in python 3.6 and pytorch 1.0. We recommend using `conda` and `pip`:

```
conda create -n igsql python=3.6
conda activate igsql
pip install -r requirements.txt
```

Download pretrained BERT model from [here](https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip) and put `bert_model.ckpt.data-00000-of-00001` into `model/bert_cn/`.

```
export BERT_BASE_DIR=moder/bert_cn

python convert_tf_checkpoint_to_pytorch.py \
  --tf_checkpoint_path $BERT_BASE_DIR/bert_model.ckpt.data-00000-of-00001 \
  --bert_config_file $BERT_BASE_DIR/bert_config_L-12_H-768_A-12.json \
  --pytorch_dump_path $BERT_BASE_DIR/pytorch_model_L-12_H-768_A-12.bin
```

### Run SeSQL experiment

Put the SeSQL data under `data/SeSQL`. 
Make sure the `entities.txt` is under `data/`. 

Run the preprocess code
> cd data/SeSQL && python generate_split_ids.py
> cd ../.. && python run/preprocess.py --dataset SeSQL --remove_from

- to train the model with editsql: run `bash scripts/train.sh`. We saved our experimental logs at `log/`. 
- to evaluate the best model: run `bash scripts/evaluate.sh`.
