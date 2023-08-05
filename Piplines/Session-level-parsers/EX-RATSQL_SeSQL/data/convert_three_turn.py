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
            if j:
                temp_question_lst=(sparc[-1]['question'] + sparc[-2]['question']).split(">>>")[:-1]
                if(len(temp_question_lst)>3):
                    temp_question_lst=temp_question_lst[:3]
                    sparc[-1]['question'] = ">>>".join(temp_question_lst)+">>>"
                else:
                    sparc[-1]['question'] = sparc[-1]['question'] + sparc[-2]['question']
            sparc[-1]['sql'] = turn['sql']
    path = './data/SeSQL_three_turn_data'
    with open(os.path.join(path, split) + '.json', 'w') as f:
        json.dump(sparc, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    for split in ['train', 'dev']:
        main(split)
