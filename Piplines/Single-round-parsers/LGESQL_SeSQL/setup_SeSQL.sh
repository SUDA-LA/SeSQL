conda create -n text2sql python=3.6
source activate text2sql
pip install torch==1.10.2+cu113 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements_SeSQL.txt
python -c "import stanza; stanza.download('zh')"
python -c "import nltk; nltk.download('stopwords')"
mkdir -p pretrained_models && cd pretrained_models
git lfs install
git clone https://huggingface.co/bert-base-chinese