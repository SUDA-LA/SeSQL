# LGESQL

Our code is mainly adapted in the released [LGESQL](https://github.com/X-LANCE/text2sql-lgesql.git).
Our main change is to adapt Chinese, for other details, please refer to the original LGESQL.

## Create environment and download dependencies

1. Firstly, create conda environment `text2sql`:
  - In our experiments, we use **torch==1.12.1+cu113** and **dgl-cu110==0.6.1** (please note that the versions of torch and dgl should match)
  - We use one Tesla V100-PCIE-32GB for base-series pre-trained language model~(PLM) experiments
    
        conda env create -f lgesql.yaml
        conda activate lgesql

2. Next, download dependencies:

        python -c "import stanza; stanza.download('zh')"
        python -c "import nltk; nltk.download('stopwords')"

3. Download pre-trained language models from [`Hugging Face Model Hub`](https://huggingface.co/models), such as `bert-base-chinese`, into the `pretrained_models` directory. (please ensure that `Git LFS` is installed)

        mkdir -p pretrained_models && cd pretrained_models
        git lfs install
        git clone https://huggingface.co/bert-base-chinese

## Download and preprocess dataset

1. Download, unzip and rename the SeSQL.zip into the directory `data`, make sure that the data used is single-round.

2. Preprocess the train, dev and test dataset, including input normalization, schema linking, graph construction and output actions generation.

        bash run/run_preprocessing.sh

## Training

Training LGESQL models with BERT respectively:
  - msde: mixed static and dynamic embeddings
  - mmc: multi-head multi-view concatenation

        bash run/run_lgesql_plm.sh [mmc|msde] bert-base-chinese

## Evaluation and submission

1. Create the directory `saved_models`, save the trained model and its configuration (at least containing `model.bin` and `params.json`) into a new directory under `saved_models`, e.g. `saved_models/bert-base-msde/`.

2. For evaluation, see `run/run_evaluation.sh` (eval from scratch) for reference.

