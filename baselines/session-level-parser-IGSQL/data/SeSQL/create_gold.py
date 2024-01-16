import os
import json

def create_gold(json_file, gold_file, db_id_file):
    with open(db_id_file, encoding='utf-8') as f:
        database_id_list = f.readlines()
        database_id_list = [db_id.strip() for db_id in database_id_list]

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    gold_query = {}
    for i, interaction in enumerate(data):
        database_id = interaction['database_id']
        if database_id not in gold_query:
            gold_query[database_id] = []
        query_interaction = []
        for turn in interaction['interaction']:
            query_interaction.append(turn['query'].replace('\n', ' '))
        gold_query[database_id].append(query_interaction)

    with open(gold_file, 'w', encoding='utf-8') as f:
        for i, database_id in enumerate(database_id_list):
            for j, interaction in enumerate(gold_query[database_id]):
                for query in interaction:
                    f.write('{}\t{}\n'.format(query, database_id))
                if not(i == len(database_id_list) - 1 and j == len(gold_query[database_id]) - 1):
                    f.write('\n')
        f.write('\n')


train_json = 'train.json'
train_gold = 'train_gold.txt'
train_db_id = 'train_db_ids.txt'

create_gold(train_json, train_gold, train_db_id)

dev_json = 'dev.json'
dev_gold = 'dev_gold.txt'
dev_db_id = 'dev_db_ids.txt'

create_gold(dev_json, dev_gold, dev_db_id)

test_json  = 'test.json'
test_gold  = 'test_gold.txt'
test_db_id = 'test_db_ids.txt'

create_gold(test_json, test_gold, test_db_id)
