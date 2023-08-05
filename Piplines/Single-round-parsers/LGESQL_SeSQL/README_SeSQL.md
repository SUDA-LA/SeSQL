# LGESQL

This is the project containing source code for the paper [*LGESQL: Line Graph Enhanced Text-to-SQL Model with Mixed Local and Non-Local Relations*](https://arxiv.org/abs/2004.12299) in **ACL 2021 main conference**. If you find it useful, please cite our work.

        @inproceedings{cao-etal-2021-lgesql,
                title = "{LGESQL}: Line Graph Enhanced Text-to-{SQL} Model with Mixed Local and Non-Local Relations",
                author = "Cao, Ruisheng  and
                Chen, Lu  and
                Chen, Zhi  and
                Zhao, Yanbin  and
                Zhu, Su  and
                Yu, Kai",
                booktitle = "Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers)",
                month = aug,
                year = "2021",
                address = "Online",
                publisher = "Association for Computational Linguistics",
                url = "https://aclanthology.org/2021.acl-long.198",
                doi = "10.18653/v1/2021.acl-long.198",
                pages = "2541--2555",
        }


## Create environment and download dependencies
The following commands are provided in `setup_SeSQL.sh`.

1. Firstly, create conda environment `text2sql`:
  - In our experiments, we use **torch==1.10.2+cu113** and **dgl-cu110==0.6.1** with CUDA version 11.3
  - We use one Tesla V100-PCIE-32GB for base-series pre-trained language model~(PLM) experiments
    
        conda create -n text2sql python=3.6
        source activate text2sql
        pip install torch==1.10.2+cu113 -f https://download.pytorch.org/whl/torch_stable.html
        pip install -r requirements_SeSQL.txt

2. Next, download dependencies:

        python -c "import stanza; stanza.download('zh')"
        python -c "import nltk; nltk.download('stopwords')"

3. Download pre-trained language models from [`Hugging Face Model Hub`](https://huggingface.co/models), such as `bert-base-chinese`, into the `pretrained_models` directory. (please ensure that `Git LFS` is installed)

        mkdir -p pretrained_models && cd pretrained_models
        git lfs install
        git clone https://huggingface.co/bert-base-chinese

## Download and preprocess dataset

1. Download, unzip and rename the SeSQL.zip into the directory `data`.

2. Preprocess the train, dev and test dataset, including input normalization, schema linking, graph construction and output actions generation.

        ./run/run_preprocessing_SeSQL.sh

## Training

Training LGESQL models with BERT respectively:
  - msde: mixed static and dynamic embeddings
  - mmc: multi-head multi-view concatenation

        ./run/run_lgesql_plm.sh [mmc|msde] bert-base-chinese

## Evaluation and submission

1. Create the directory `saved_models`, save the trained model and its configuration (at least containing `model.bin` and `params.json`) into a new directory under `saved_models`, e.g. `saved_models/bert-base-msde/`.

2. For evaluation, see `run/run_evaluation.sh` (eval from scratch) for reference.

## Results
Dev and test **EXACT MATCH ACC** are provided below:

| model | dev acc | test acc |
| :---: | :---: | :---: |
| LGESQL + BERT | 76.8 | 71.0 |

## Acknowledgements

We would like to thank Tao Yu, Yusen Zhang and Bo Pang for running evaluations on our submitted models. We are also grateful to the flexible semantic parser [TranX](https://github.com/pcyin/tranX) that inspires our works.