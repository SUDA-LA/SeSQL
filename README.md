# SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset

[English](README.en.md) | 简体中文

## 引用
如果您认为我们的工作对您的工作有帮助，请引用我们的论文：

#### SeSQL: A High-quality Large-scale Session-level Chinese Text-to-SQL Dataset (Accepted by NLPCC 2023 main conference)

## 简介

Text-to-SQL语义解析旨在基于给定的数据库，将自然语言问题转化成SQL语句。通过对Text-to-SQL语义解析技术进行研究，可以帮助数据相关的从业人员更加简单地使用数据库检索信息，也可以推动智能交互技术的发展，为人机交互和智能客服等领域提供强大的技术支持，还能广泛应用于搜索引擎、语音助手等产品。

之前的研究主要集中在单轮Text-to-SQL语义解析技术上，其输入的问题是上下文无关的，常用的数据集有英文的WikiSQL、Spider和中文的DuSQL。然而，在现实环境中，用户通常很难通过一个单独的问题来查询到所需的信息， 因此最近的工作开始研究会话级Text-to-SQL语义解析，会话级Text-to-SQL语义解析旨在多轮对话中解析自然语言问题并生成对应的SQL语句。

目前的数据集包括英文的CoSQL、SparC，以及中文的CHASE。为了缓解CHASE数据集中存在的问题，本仓库提供了一个高质量大规模的会话级中文Text-to-SQL数据集**SeSQL**，包含5,028个会话和27,012个问题/SQL对，所以会话都是人工从头开始构建的。除此之外，我们还额外提供了如下资源：

+ **中文Text-to-SQL基线模型`./Piplines`**：
  + **会话级解析模型`./Piplines/Session-level-parsers`**：包括论文中介绍的三个具有代表性的开源会话级解析模型，[EditSQL](https://github.com/ryanzhumich/editsql)、[IGSQL](https://github.com/headacheboy/IGSQL)和Guo等人(2021)提出的扩展的RATSQL（[EX-RATSQL](https://github.com/xjtu-intsoft/chase)）。
    + 我们对这些英文上的会话级解析模型进行了一些修改，以便使其支持中文会话级Text-to-SQL语义解析和适配我们的SeSQL数据集。
  + **单轮解析模型`./Piplines/Single-round-parsers`**：包括论文中介绍的在英文Spider数据集上具有竞争力的开源的单轮解析模型[LGESQL](https://github.com/rhythmcao/text2sql-lgesql)，利用Dual RGAT对问题和数据库模式进行联合编码，并提出了一个图剪枝辅助任务。
    + 我们对单轮Text-to-SQL语义解析模型LGESQL的代码进行了一部分修改，以使其能够支持中文单轮Text-to-SQL语义解析和适配我们的SeSQL数据集。
    + LGESQL模型是根据SeSQL数据集中补全的上下文无关数据进行训练和评估的。
+ **SeSQL数据集示例`./Examples`**：
  + 示例文件包含来自SeSQL数据集的一些例子。
    + **数据库内容文件`./Examples/db_content.json`**：存储数据库的内容信息，包含了数据库中每个表的内容数据。
    + **数据库模式文件`./Examples/tables.json`**：存储数据库的表结构信息，包含了数据库中每个表的结构数据。
    + **会话级数据集文件`./Examples/SeSQL_session_examples.json`**：存储会话级Text-to-SQL涉及到的自然语言问题、SQL语句和相应的数据库信息，还包含了主题转换、上下文相关类别以及补全的独立问题，用于会话级模型训练。
    + **单轮数据集文件`./Examples/SeSQL_single_examples.json`**：存储单轮Text-to-SQL涉及到的自然语言问题、SQL语句和相应数据库信息，用于单轮模型训练。

## SeSQL数据集

我们基于会话级Text-to-SQL语义解析任务，制定相关标注规范，采用迭代交叉标注加审核专家审核的方法，从头开始人工标注，构建了一个高质量、大规模的会话级中文Text-to-SQL数据集SeSQL。
SeSQL数据集有以下几个重要的特征：
1）我们采用迭代交叉标注加审核专家审核的方法，从头构建SeSQL数据集，保证对之前提交的内容进行仔细和及时的审核，这对提高数据质量十分有效，大大提升了我们数据集的质量。
2）我们设计了七种类型的主题转换来指导标注者创建下一个SQL查询语句。
3）我们人工标注了相邻自然语言问题之间的上下文相关性，比如省略和共指。
4）我们对会话级解析中上下文相关的问题进行了补全，得到了27,012个独立问题，使SeSQL数据集可用于中文单轮Text-to-SQL语义解析和问题补全技术研究。

数据集的整体统计如下表所示：
| Dataset | DBs | Tables | Sequences | Pairs | Average round | Dependent Ratio | Easy Ratio |
| :------: | :---------: | :---------: | :---------: | :---------: |  :---------: |  :---------: |  :---------: |
| SeSQL | 201 | 813 | 5,028 | 27,012 | 5.4 | 65.5 | 13.6 |

更多关于SeSQL数据集的细节，请参考我们的论文。

**注：由于一些原因，目前SeSQL数据集暂未发布，如果您需要SeSQL数据集，请联系我们的第一作者或通讯作者。**

## 基线模型

关于基线模型实验环境的配置和模型的训练、评估，请参照`./Piplines`中相关模型的README.md。

### 实验结果：

|                         Models                         | Dev QM | Test QM | Dev IM | Test IM |
| :----------------------------------------------------: | :----: | :-----: | :----: | :-----: |
|   [EditSQL](https://github.com/ryanzhumich/editsql)    |  57.2  |  52.6   |  27.3  |  22.6   |
|     [IGSQL](https://github.com/headacheboy/IGSQL)      |  63.3  |  59.5   |  35.0  |  29.0   |
|   [EX-RATSQL](https://github.com/xjtu-intsoft/chase)   |  56.6  |  50.4   |  18.9  |  17.0   |
| [LGESQL](https://github.com/rhythmcao/text2sql-lgesql) |  76.8  |  71.0   | -----  |  -----  |

## 联系
如果您在使用我们的数据集及代码的过程中遇到了任何问题，可联系saihaohuang@qq.com。
