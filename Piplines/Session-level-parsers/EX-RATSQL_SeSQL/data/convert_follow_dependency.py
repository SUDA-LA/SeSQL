import json
import os
import shutil


def main(split):
    with open('./data/' + split + '.json') as f:
        data = json.load(f)
    sparc = []
    for i in range(len(data)):
        d = data[i]
        for j in range(len(d['interaction'])):
            turn = d['interaction'][j]
            sparc.append({})
            sparc[-1]['interaction_id'] = i + 1
            sparc[-1]['turn_id'] = j + 1
            sparc[-1]['db_id'] = d['database_id']
            sparc[-1]['query'] = turn['query']
            sparc[-1]['question'] = turn['utterance'].replace('“', '\"').replace('”', '\"').replace('‘', '\"').replace('’', '\"') + '>>>'
            sparc[-1]["contextual_phenomena"]=turn["contextual_phenomena"]
            sparc[-1]["category"]=turn["category"]
            if j:
                if(sparc[-1]["contextual_phenomena"]!=["Independent"] and sparc[-1]["contextual_phenomena"]!=["Only Dependent"]):
                    sparc[-1]['question'] = sparc[-1]['question'] + sparc[-2]['question']
            sparc[-1]['sql'] = turn['sql']
    path = './data/SeSQL_follow_dependency_data'
    with open(os.path.join(path, split) + '.json', 'w') as f:
        json.dump(sparc, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    for split in ['train', 'dev', 'test']:
        main(split)
