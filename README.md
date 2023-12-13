# SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset


## Introduction

**SeSQL** provides a high-quality and large-scale session-level Chinese Text-to-SQL dataset, which contains 5,028 sessions and 27,012 question/SQL pairs. All sessions in SeSQL are manually constructed from scratch. In addition, we also provide the following resources:

+ **SeSQL Dataset `data/`**:
  + `db_content.json`: Full databases with contents (values). 
  + `tables.json`: The schemas for the databases. 
  + `train/dev/test.json`: The train/dev/test datasets (after splt). 
  + `single-round-question-completed/`: The completed context-independent SeSQL dataset (i.g., single-round), also including `train/dev/test` splits.
  + `SeSQL.zip`: The compress file for the above contents. 
  + `examples/`: Dataset examples:
    + Example file contains some examples from the SeSQL dataset and you can preview them on GitHub.
      + **Database Content File `db_content.json`**: Store the content information of the database, including the content data of each table in the database.
      + **Database Schema File `tables.json`**: Store the table structure information of the database, including the structural data of each table in the database.
      + **Session-level Dataset File `session_level_examples.json`**: Store natural language questions, SQL statements, and corresponding database information involved in session-level Text-to-SQL, including thematic transition, context-dependent types, and completed independent questions, used for session-level model training.
      + **Single-round Dataset File `single_round_examples.json`**:  Store natural language questions, SQL statements, and corresponding database information involved in single-round Text-to-SQL, used for single-round model training.
+ **Chinese Text-to-SQL Baseline Models `baselines/`**:
  + **Session-level Parsing Models `session-level-parser-IGSQL`**: the representative open-source session-level parsing model [IGSQL](https://github.com/headacheboy/IGSQL)
    + We have made some modifications to these English session-level parsing models to support Chinese session-level Text-to-SQL semantic parsing and to fit our SeSQL dataset.
  + **Single-round Parsing Models `single-round-parser-LGESQL`**: It includes the competitive open-source single-round parsing model [LGESQL](https://github.com/rhythmcao/text2sql-lgesql) on the English Spider dataset, which utilizes Dual RGAT to jointly encode the questions and database schemas, and proposes a graph pruning auxiliary task.
    + We have partially modified the code of the single-round Text-to-SQL semantic parsing model LGESQL to support Chinese single-round Text-to-SQL semantic parsing and to fit our SeSQL dataset.
    + LGESQL is trained and evaluated on the completed context-independent data in the SeSQL dataset.


For more details, please see our [paper](https://arxiv.org/abs/2208.12711). 

## Evaluation

We provide the session-level and single-round evaluations under `scripts/`. 

For evaluation, the only dependency is `nltk` and you can simply run `pip install nltk` to get it. 

> bash scripts/evaluation_session_level.py         # eval the session-level prediction
> 
> bash scripts/eval_single_round.sh                # eval the single-round prediction

For path settings, please check in `/scripts`. 

## Baselines

The usages of baseline models (including preprocess, traning, and evaluation) are availabel in README under each baseline directory. 

## Citation

If you find this work is useful for your research, please cite our paper:

#### SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset (Accepted by NLPCC 2023 main conference)

## Contact
If you have any problems, please make an issue or contact us at saihaohuang@qq.com / yanggangu@outlook.com. 

