""" Utility functions for loading and processing ATIS data."""
import os
import random
import json

from . import anonymization as anon
from . import atis_batch
from . import dataset_split as ds

from .interaction import load_function
from .entities import NLtoSQLDict
from .atis_vocab import ATISVocabulary

ENTITIES_FILENAME = 'data/entities.txt'
ANONYMIZATION_FILENAME = 'data/anonymization.txt'

class ATISDataset():    
    """ Contains the ATIS data. """
    def __init__(self, params):
        self.anonymizer = None
        if params.anonymize:    # params.anonymize = False，这个参数不知道有啥用
            self.anonymizer = anon.Anonymizer(ANONYMIZATION_FILENAME)

        if not os.path.exists(params.data_directory):   # params.data_directory = 'processed_data_chase_removefrom'
            os.mkdir(params.data_directory)

        # ************************************************************************************
        # 这个字典是一个命名实体的字典，主要是关于英文的，有几个经典操作（ TODO 不全 ）：
        # 把序数词或者月份处理成更为普遍的数字或词，例如"march"处理成"3"
        # 把小写的命名实体大写化，例如"new york"处理成"NEW YORK"
        # 把一个命名实体不同的形态处理成一样，例如"new york"和"new york city"处理成"NEW YORK"
        # 例如，会把"flights"，处理成[['DISTINCT', 'flight.flight_id', 'FROM', 'flight'], ...]， TODO 我不知道对text2sql任务有什么帮助
        self.entities_dictionary = NLtoSQLDict(ENTITIES_FILENAME)   # 加载一个NL2SQL的字典
        # print(self.entities_dictionary.entity_dict["flights"])  # 一个实体可能在字典里映射多个替代
        # ************************************************************************************

        # ************************************************************************************
        # 这一部分是读取schema信息，也就是tables.json存储的东西
        # database_schema：长度为280的字典，key为db名，value为字典，value的字典包含table.json里面的内容，table_names/column_names/primary_keys...
        # column_names_surface_form：一个长度为8296的列表，全部的"tab.col"捆绑的信息，例如："场馆.场馆编号"
        # column_names_embedder_input：同样长度为8296的列表，存的也是"tab.col"捆绑的信息，不过每个列表元素存的是切割的token，例如：['场馆', '.', '场馆编号']
        database_schema = None
        if params.database_schema_filename: # params.database_schema_filename = 'data/chase_data_removefrom/tables.json'
            if 'removefrom' not in params.data_directory:
                database_schema, column_names_surface_form, column_names_embedder_input = self.read_database_schema_simple(params.database_schema_filename)
            else:
                database_schema, column_names_surface_form, column_names_embedder_input = self.read_database_schema(params.database_schema_filename)
        # ************************************************************************************

        # 这是返回了一个函数对象
        int_load_function = load_function(params,
                                          self.entities_dictionary,
                                          self.anonymizer,
                                          database_schema=database_schema)

        # 这个函数是用来把嵌套的列表变成一个列表
        def collapse_list(the_list):
            """ Collapses a list of list into a single list."""
            return [s for i in the_list for s in i]

        if 'atis' not in params.data_directory:   # params.data_directory = 'processed_data_chase_removefrom'
            # ************************************************************************************
            # 这是用来载入train和valid数据集的工具
            # self.train_data对象有一个列表元素examples，长度3949
            # self.valid_data对象中的examples，长度755
            # examples的列表元素对象，内容：
            #   1.identifier：例如'中国城市/0'，前面是db名字，后面是此db第几次出现
            #   2.anon_tok_to_ent： TODO
            #   3.snippets： TODO
            #   4.schema：2个列表2个字典，其中两个字典是和列表对应的映射字典，两个列表存值，例如'省份 . 省份id'和'省份.省份id'，中间其中一个拿空格隔开，方便后面embedding
            #   5.utterances：一个session的交互内容列表，每个列表元素对象有gold query的token列表，question的token列表等
            self.train_data = ds.DatasetSplit(
                os.path.join(params.data_directory, params.processed_train_filename), # params.processed_train_filename = 'train.pkl'
                params.raw_train_filename,
                int_load_function)
            self.valid_data = ds.DatasetSplit(
                os.path.join(params.data_directory, params.processed_validation_filename),
                params.raw_validation_filename,
                int_load_function)
            if params.raw_test_filename:  
                self.test_data = ds.DatasetSplit(
                    os.path.join(params.data_directory, params.processed_test_filename),
                    params.raw_test_filename,
                    int_load_function)
            # ************************************************************************************

            s = set()
            for ele in self.train_data.examples:
                s.add(ele.schema.table_schema['db_id'])
            db_id_ls = list(s) # train数据集的db列表
            db_id_ls.sort()
            self.id2db= db_id_ls
            self.db2id = {}
            for i in range(len(self.id2db)):
                self.db2id[self.id2db[i]] = i

            # train_input_seqs列表长度为12914，valid_input_seqs列表长度为2494，
            # 存放元素：[['哪', '个', '城', '市', '的', '人', '口', '最', '多', '？'], ...]
            train_input_seqs = collapse_list(self.train_data.get_ex_properties(lambda i: i.input_seqs()))
            valid_input_seqs = collapse_list(self.valid_data.get_ex_properties(lambda i: i.input_seqs()))
            # if params.raw_test_filename:
            #     test_input_seqs = collapse_list(self.test_data.get_ex_properties(lambda i: i.input_seqs()))

            # all_input_seqs列表长度为12914 + 2494 = 15408
            all_input_seqs = train_input_seqs + valid_input_seqs
            # if params.raw_test_filename:
            #     all_input_seqs = train_input_seqs + valid_input_seqs + test_input_seqs

            # ATISVocabulary有两个模式，一个是input一个是schema
            # input词典对象一共有3个元素：
            #   inorder_tokens：长度为2709的列表，有'_UNK'/'_EOS'这样的特殊词
            #   tokens：长度为2709的集合
            #   raw_vocab：拥有一些功能元素，词典的id和token的映射，最少出现次数，最大长度，还有功能性的token，'_UNK'/'_EOS'/';'
            # 特殊的功能token是超参数，在这套代码有预置的3个
            self.input_vocabulary = ATISVocabulary(
                all_input_seqs,
                os.path.join(params.data_directory, params.input_vocabulary_filename),
                params,
                is_input='input',
                anonymizer=self.anonymizer if params.anonymization_scoring else None)

            # schema词典对象也是3个元素：
            #   inorder_tokens：长度为4087的列表，列表存schema中的列名表名和'*'、'.'等
            #   tokens：长度为4087的集合
            #   raw_vocab：和上面那个一致
            # 特殊词只剩下'_UNK'
            # params.processed_train_filename = 'train.pkl'，params.output_vocabulary_filename = 'output_vocabulary.pkl'
            self.output_vocabulary_schema = ATISVocabulary(
                column_names_embedder_input,
                os.path.join(params.data_directory, 'schema_'+params.output_vocabulary_filename),
                params,
                is_input='schema',
                anonymizer=self.anonymizer if params.anonymization_scoring else None)

            # train_output_seqs列表长度为12914，valid_output_seqs列表长度为2494，all_output_seqs列表长度为15408
            # 存放元素：[['select', '城市.名称', 'order_by', '城市.人口', 'desc', 'limit_value'], ...]
            train_output_seqs = collapse_list(self.train_data.get_ex_properties(lambda i: i.output_seqs()))
            valid_output_seqs = collapse_list(self.valid_data.get_ex_properties(lambda i: i.output_seqs()))
            all_output_seqs = train_output_seqs + valid_output_seqs
            # if params.raw_test_filename:
            #     test_output_seqs = collapse_list(self.test_data.get_ex_properties(lambda i: i.output_seqs()))
            #     all_output_seqs = train_output_seqs + valid_output_seqs + test_output_seqs

            # sql_keywords是指sql出现的关键字，共51个
            sql_keywords = ['.', 't1', 't2', '=', 'select', 'as', 'join', 'on', ')', '(', 'where', 't3', 'by', ',', 'group', 'distinct', 't4', 'and', 'limit', 'desc', '>', 'avg', 'having', 'max', 'in', '<', 'sum', 't5', 'intersect', 'not', 'min', 'except', 'or', 'asc', 'like', '!', 'union', 'between', 't6', '-', 't7', '+', '/']
            sql_keywords += ['count', 'from', 'value', 'order']
            sql_keywords += ['group_by', 'order_by', 'limit_value', '!=']
            sql_keywords += [">=", "<="]    # TODO SeSQL特有的

            # skip column_names_surface_form but keep sql_keywords
            skip_tokens = list(set(column_names_surface_form) - set(sql_keywords))

            if params.data_directory == 'processed_data_sparc_removefrom_test':
              all_output_seqs = []
              out_vocab_ordered = ['select', 'value', ')', '(', 'where', '=', ',', 'count', 'group_by', 'order_by', 'limit_value', 'desc', '>', 'distinct', 'avg', 'and', 'having', '<', 'in', 'max', 'sum', 'asc', 'like', 'not', 'or', 'min', 'intersect', 'except', '!=', 'union', 'between', '-', '+']
              for i in range(len(out_vocab_ordered)):
                all_output_seqs.append(out_vocab_ordered[:i+1])

            # output_vocabulary是sql关键词的字典，还包括'_UNK'/'_EOS'，共35个
            self.output_vocabulary = ATISVocabulary(
                all_output_seqs,
                os.path.join(params.data_directory, params.output_vocabulary_filename),
                params,
                is_input='output',
                anonymizer=self.anonymizer if params.anonymization_scoring else None,
                skip=skip_tokens)
        else:
            self.train_data = ds.DatasetSplit(
                os.path.join(params.data_directory, params.processed_train_filename),
                params.raw_train_filename,
                int_load_function)
            if params.train:
                self.valid_data = ds.DatasetSplit(
                    os.path.join(params.data_directory, params.processed_validation_filename),
                    params.raw_validation_filename,
                    int_load_function)
            if params.evaluate or params.attention:
                self.dev_data = ds.DatasetSplit(
                    os.path.join(params.data_directory, params.processed_dev_filename),
                    params.raw_dev_filename,
                    int_load_function)
                if params.enable_testing:
                    self.test_data = ds.DatasetSplit(
                        os.path.join(params.data_directory, params.processed_test_filename),
                        params.raw_test_filename,
                        int_load_function)

            train_input_seqs = []
            train_input_seqs = collapse_list(
                self.train_data.get_ex_properties(
                    lambda i: i.input_seqs()))

            self.input_vocabulary = ATISVocabulary(
                train_input_seqs,
                os.path.join(params.data_directory, params.input_vocabulary_filename),
                params,
                is_input='input',
                min_occur=2,
                anonymizer=self.anonymizer if params.anonymization_scoring else None)

            train_output_seqs = collapse_list(
                self.train_data.get_ex_properties(
                    lambda i: i.output_seqs()))

            self.output_vocabulary = ATISVocabulary(
                train_output_seqs,
                os.path.join(params.data_directory, params.output_vocabulary_filename),
                params,
                is_input='output',
                anonymizer=self.anonymizer if params.anonymization_scoring else None)

            self.output_vocabulary_schema = None

    def read_database_schema_simple(self, database_schema_filename):
        with open(database_schema_filename, "r", encoding="utf-8") as f:
            database_schema = json.load(f)

        database_schema_dict = {}
        column_names_surface_form = []
        column_names_embedder_input = []
        for table_schema in database_schema:
            db_id = table_schema['db_id']
            database_schema_dict[db_id] = table_schema

            column_names = table_schema['column_names']
            column_names_original = table_schema['column_names_original']
            table_names = table_schema['table_names']
            table_names_original = table_schema['table_names_original']

            for i, (table_id, column_name) in enumerate(column_names_original):
                column_name_surface_form = column_name
                column_names_surface_form.append(column_name_surface_form.lower())

            for table_name in table_names_original:
                column_names_surface_form.append(table_name.lower())

            for i, (table_id, column_name) in enumerate(column_names):
                column_name_embedder_input = column_name
                column_names_embedder_input.append(column_name_embedder_input.split())

            for table_name in table_names:
                column_names_embedder_input.append(table_name.split())

        database_schema = database_schema_dict

        return database_schema, column_names_surface_form, column_names_embedder_input

    def read_database_schema(self, database_schema_filename):
        with open(database_schema_filename, "r", encoding="utf-8") as f:
            database_schema = json.load(f)

        database_schema_dict = {}
        column_names_surface_form = []
        column_names_embedder_input = []
        for table_schema in database_schema:
            db_id = table_schema['db_id']
            database_schema_dict[db_id] = table_schema

            column_names = table_schema['column_names']
            column_names_original = table_schema['column_names_original']
            table_names = table_schema['table_names']
            table_names_original = table_schema['table_names_original']

            for i, (table_id, column_name) in enumerate(column_names_original):
                if table_id >= 0:
                    table_name = table_names_original[table_id]
                    column_name_surface_form = '{}.{}'.format(table_name,column_name)
                else:
                    column_name_surface_form = column_name
                column_names_surface_form.append(column_name_surface_form.lower())

            # also add table_name.*
            for table_name in table_names_original:
                column_names_surface_form.append('{}.*'.format(table_name.lower()))

            for i, (table_id, column_name) in enumerate(column_names):
                if table_id >= 0:
                    table_name = table_names[table_id]
                    column_name_embedder_input = table_name + ' . ' + column_name
                else:
                    column_name_embedder_input = column_name
                column_names_embedder_input.append(column_name_embedder_input.split())

            for table_name in table_names:
                column_name_embedder_input = table_name + ' . *'
                column_names_embedder_input.append(column_name_embedder_input.split())

        database_schema = database_schema_dict

        return database_schema, column_names_surface_form, column_names_embedder_input

    def get_all_utterances(self,
                           dataset,
                           max_input_length=float('inf'),
                           max_output_length=float('inf')):
        """ Returns all utterances in a dataset."""
        items = []
        for interaction in dataset.examples:
            for i, utterance in enumerate(interaction.utterances):
                if utterance.length_valid(max_input_length, max_output_length):
                    items.append(atis_batch.UtteranceItem(interaction, i))
        return items

    def get_all_interactions(self,
                             dataset,
                             max_interaction_length=float('inf'),
                             max_input_length=float('inf'),
                             max_output_length=float('inf'),
                             sorted_by_length=False):
        """Gets all interactions in a dataset that fit the criteria.

        Inputs:
            dataset (ATISDatasetSplit): The dataset to use.
            max_interaction_length (int): Maximum interaction length to keep.
            max_input_length (int): Maximum input sequence length to keep.
            max_output_length (int): Maximum output sequence length to keep.
            sorted_by_length (bool): Whether to sort the examples by interaction length.
        """
        ints = [
            atis_batch.InteractionItem(
                interaction,
                max_input_length,
                max_output_length,
                self.entities_dictionary,
                max_interaction_length) for interaction in dataset.examples]
        if sorted_by_length:
            return sorted(ints, key=lambda x: len(x))[::-1]
        else:
            return ints

    # This defines a standard way of training: each example is an utterance, and
    # the batch can contain unrelated utterances.
    def get_utterance_batches(self,
                              batch_size,
                              max_input_length=float('inf'),
                              max_output_length=float('inf'),
                              randomize=True):
        """Gets batches of utterances in the data.

        Inputs:
            batch_size (int): Batch size to use.
            max_input_length (int): Maximum length of input to keep.
            max_output_length (int): Maximum length of output to use.
            randomize (bool): Whether to randomize the ordering.
        """
        # First, get all interactions and the positions of the utterances that are
        # possible in them.
        items = self.get_all_utterances(self.train_data,
                                        max_input_length,
                                        max_output_length)
        if randomize:
            random.shuffle(items)

        batches = []

        current_batch_items = []
        for item in items:
            if len(current_batch_items) >= batch_size:
                batches.append(atis_batch.UtteranceBatch(current_batch_items))
                current_batch_items = []
            current_batch_items.append(item)
        batches.append(atis_batch.UtteranceBatch(current_batch_items))

        assert sum([len(batch) for batch in batches]) == len(items)

        return batches

    def get_interaction_batches(self,
                                batch_size,
                                max_interaction_length=float('inf'),
                                max_input_length=float('inf'),
                                max_output_length=float('inf'),
                                randomize=True):
        """Gets batches of interactions in the data.

        Inputs:
            batch_size (int): Batch size to use.
            max_interaction_length (int): Maximum length of interaction to keep
            max_input_length (int): Maximum length of input to keep.
            max_output_length (int): Maximum length of output to keep.
            randomize (bool): Whether to randomize the ordering.
        """
        items = self.get_all_interactions(self.train_data,
                                          max_interaction_length,
                                          max_input_length,
                                          max_output_length,
                                          sorted_by_length=not randomize)
        if randomize:
            random.shuffle(items)

        batches = []
        current_batch_items = []
        for item in items:
            if len(current_batch_items) >= batch_size:
                batches.append(
                    atis_batch.InteractionBatch(current_batch_items))
                current_batch_items = []
            current_batch_items.append(item)
        batches.append(atis_batch.InteractionBatch(current_batch_items))

        assert sum([len(batch) for batch in batches]) == len(items)

        return batches

    def get_random_utterances(self,
                              num_samples,
                              max_input_length=float('inf'),
                              max_output_length=float('inf')):
        """Gets a random selection of utterances in the data.

        Inputs:
            num_samples (bool): Number of random utterances to get.
            max_input_length (int): Limit of input length.
            max_output_length (int): Limit on output length.
        """
        items = self.get_all_utterances(self.train_data,
                                        max_input_length,
                                        max_output_length)
        random.shuffle(items)
        return items[:num_samples]

    def get_random_interactions(self,
                                num_samples,
                                max_interaction_length=float('inf'),
                                max_input_length=float('inf'),
                                max_output_length=float('inf')):

        """Gets a random selection of interactions in the data.

        Inputs:
            num_samples (bool): Number of random interactions to get.
            max_input_length (int): Limit of input length.
            max_output_length (int): Limit on output length.
        """
        items = self.get_all_interactions(self.train_data,
                                          max_interaction_length,
                                          max_input_length,
                                          max_output_length)
        random.shuffle(items)
        return items[:num_samples]


def num_utterances(dataset):
    """Returns the total number of utterances in the dataset."""
    return sum([len(interaction) for interaction in dataset.examples])
