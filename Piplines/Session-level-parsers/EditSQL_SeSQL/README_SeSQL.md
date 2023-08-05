### Dependency

The model is tested in python 3.6 and pytorch 1.0. We recommend using `conda` and `pip`:

```
conda create -n editsql python=3.6
conda activate editsql
pip install -r requirements.txt
```

Download pretrained BERT model from [here](https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip) and put `bert_model.ckpt.data-00000-of-00001` into `model/bert_cn/`.

```
export BERT_BASE_DIR=model/bert_cn

python convert_tf_checkpoint_to_pytorch.py \
  --tf_checkpoint_path $BERT_BASE_DIR/bert_model.ckpt.data-00000-of-00001 \
  --bert_config_file $BERT_BASE_DIR/bert_config_L-12_H-768_A-12.json \
  --pytorch_dump_path $BERT_BASE_DIR/pytorch_model_L-12_H-768_A-12.bin
```

Download pretrained word vectors GloVe from [here](http://nlp.stanford.edu/data/glove.840B.300d.zip) as `./path/to/data/glove.840B.300d.txt` and make sure `GLOVE_PATH = ./path/to/data/glove.840B.300d.txt` in `train_SeSQL.sh`.

### Run SeSQL experiment

- to train the model with editsql: run `./train_SeSQL.sh`. We saved our experimental logs at `./logs/logs_SeSQL_editsql`. 
- to evaluate the best model: run `./evaluate.sh`.