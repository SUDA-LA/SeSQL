import argparse
import json


def generate_database_ids(file_name):
    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
    database_id = set()
    for interaction in data:
        database_id.add(interaction['database_id'])
    return database_id


def create_data(in_file, out_file):
    database_id_list = list(generate_database_ids(in_file))

    with open(in_file, encoding='utf-8') as f:
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

    with open(out_file, 'w', encoding='utf-8') as f:
        for i, database_id in enumerate(database_id_list):
            for j, interaction in enumerate(gold_query[database_id]):
                for query in interaction:
                    f.write('{}\t{}\n'.format(query, database_id))
                if not(i == len(database_id_list) - 1 and j == len(gold_query[database_id]) - 1):
                    f.write('\n')
        f.write('\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--in_file', type=str)
  parser.add_argument('--out_file', type=str)
  args = parser.parse_args()

  create_data(args.in_file, args.out_file)
