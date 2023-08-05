# SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset

English | [简体中文](README.md)

## Citation

If you find this work is useful for your research, please cite our paper:

#### SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset (Accepted by NLPCC 2023 main conference)

## Introduction

Text-to-SQL semantic parsing aims to transform natural language questions into SQL queries based on given databases. Research on Text-to-SQL semantic parsing can assist data professionals in using databases to retrieve information more easily. It can also promote the development of intelligent interaction technology and provide strong technical support for human-computer interaction and intelligent customer service in various domains, and can also be widely used in search engines, voice assistants and other products.

Previous studies mainly focus on the single-round Text-to-SQL semantic parsing techniques, where the input questions are context-independent. Popular  datasets include WikiSQL and Spider for English, and DuSQL for Chinese. However, in a real-world setting, it is usually difficult for users to meet their information need via a single stand-alone question. Therefore, recent works start to tackle session-level Text-to-SQL semantic parsing, which aims to parse natural language questions and generate corresponding SQL queries in the multi-turn conversations.

Existing datasets include CoSQL and SparC for English, and CHASE for Chinese. To alleviate the issues in the CHASE dataset, this repository provides a high-quality and large-scale session-level Chinese Text-to-SQL dataset called **SeSQL**, which contains 5,028 sessions and 27,012 question/SQL pairs. All sessions in SeSQL are manually constructed from scratch. In addition, we also provide the following resources:

+ **Chinese Text-to-SQL Baseline Models`./Piplines`**:
  + **Session-level Parsing Models`./Piplines/Session-level-parsers`**: They include three representative open-source session-level parsing models introduced in the paper, [EditSQL](https://github.com/ryanzhumich/editsql), [IGSQL](https://github.com/headacheboy/IGSQL), and extended RATSQL approach proposed by Guo et al. (2021) ([EX-RATSQL](https://github.com/xjtu-intsoft/chase))
    + We have made some modifications to these English session-level parsing models to support Chinese session-level Text-to-SQL semantic parsing and to fit our SeSQL dataset.
  + **Single-round Parsing Models`./Piplines/Single-round-parsers`**: It includes the competitive open-source single-round parsing model [LGESQL](https://github.com/rhythmcao/text2sql-lgesql) on the English Spider dataset, which utilizes Dual RGAT to jointly encode the questions and database schemas, and proposes a graph pruning auxiliary task.
    + We have partially modified the code of the single-round Text-to-SQL semantic parsing model LGESQL to support Chinese single-round Text-to-SQL semantic parsing and to fit our SeSQL dataset.
    + LGESQL is trained and evaluated on the completed context-independent data in the SeSQL dataset.
+ **SeSQL Dataset Examples`./Examples`**:
  + Example file contains some examples from the SeSQL dataset.
    + **Database Content File`./Examples/db_content.json`**: Store the content information of the database, including the content data of each table in the database.
    + **Database Schema File`./Examples/tables.json`**: Store the table structure information of the database, including the structural data of each table in the database.
    + **Session-level Dataset File`./Examples/SeSQL_session_examples.json`**: Store natural language questions, SQL statements, and corresponding database information involved in session-level Text-to-SQL, including thematic transition, context-dependent types, and completed independent questions, used for session-level model training.
    + **Single-round Dataset File`./Examples/SeSQL_single_examples.json`**:  Store natural language questions, SQL statements, and corresponding database information involved in single-round Text-to-SQL, used for single-round model training.

## SeSQL Dataset

Based on the session-level Text-to-SQL semantic parsing task, we devise relevant annotation guidelines and adopte iterative cross-annotation with expert review to manually construct a high-quality, large-scale Chinese session-level Text-to-SQL dataset SeSQL. 

SeSQL dataset has the following important features:

1) We adopte iterative cross-annotation with expert review to construct the SeSQL dataset from scratch, ensuring careful and timely review of previous submission, which is highly effective in improving data quality and greatly enhancing the quality of our dataset.
2) We design seven categories of thematic transition for explicitly guiding annotators to create next-round SQL queries.
3) We explicitly annotate the context-dependent types of adjacent natural language questions, such as ellipses and co-reference.
4) We complete context-dependent questions in session-level parsing, resulting in 27,012 independent questions, making the SeSQL dataset can be used for Chinese single-round Text-to-SQL semantic parsing and question completion research.

The overall statistics of the dataset are shown in the following table:

| Dataset | DBs | Tables | Sequences | Pairs | Average round | Dependent Ratio | Easy Ratio |
| :------: | :---------: | :---------: | :---------: | :---------: |  :---------: |  :---------: |  :---------: |
| SeSQL | 201 | 813 | 5,028 | 27,012 | 5.4 | 65.5 | 13.6 |

For more details about SeSQL, please kindly refer to our paper.

**Note: Due to some reasons,  SeSQL is not published currently. If you need SeSQL, please contact the first author or corresponding author.**

## Baseline models

For the experimental setup and training/evaluation of baseline models, please refer to the README.md of relevant models in `./Piplines`

### Experimental result:

|                         Models                         | Dev QM | Test QM | Dev IM | Test IM |
| :----------------------------------------------------: | :----: | :-----: | :----: | :-----: |
|   [EditSQL](https://github.com/ryanzhumich/editsql)    |  57.2  |  52.6   |  27.3  |  22.6   |
|     [IGSQL](https://github.com/headacheboy/IGSQL)      |  63.3  |  59.5   |  35.0  |  29.0   |
|   [EX-RATSQL](https://github.com/xjtu-intsoft/chase)   |  56.6  |  50.4   |  18.9  |  17.0   |
| [LGESQL](https://github.com/rhythmcao/text2sql-lgesql) |  76.8  |  71.0   | -----  |  -----  |

## Contact
If you have any problems, feel free to contact me at saihaohuang@qq.com.
