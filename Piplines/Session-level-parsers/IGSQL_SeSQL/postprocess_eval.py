import os
import json
import sqlparse
import argparse
import subprocess
from collections import defaultdict
import traceback

def find_shortest_path(start, end, graph):
    stack = [[start, []]]
    visited = set()
    while len(stack) > 0:
        ele, history = stack.pop()
        if ele == end:
            return history
        for node in graph[ele]:
            if node[0] not in visited:
                stack.append((node[0], history + [(node[0], node[1])]))
                visited.add(node[0])


def gen_from(candidate_tables, schema):
    if len(candidate_tables) <= 1:
        if len(candidate_tables) == 1:
            ret = "from {}".format(schema["table_names_original"][list(candidate_tables)[0]])
        else:
            ret = "from {}".format(schema["table_names_original"][0])
        return {}, ret

    table_alias_dict = {}
    uf_dict = {}
    for t in candidate_tables:
        uf_dict[t] = -1
    idx = 1
    graph = defaultdict(list)   # 这个graph图应该是为了表示schema的外键关系的
    for acol, bcol in schema["foreign_keys"]:
        t1 = schema["column_names"][acol][0]
        t2 = schema["column_names"][bcol][0]
        graph[t1].append((t2, (acol, bcol)))
        graph[t2].append((t1, (bcol, acol)))
    candidate_tables = list(candidate_tables)
    start = candidate_tables[0]
    start_idx = 0 # TODO
    table_alias_dict[start] = idx
    idx += 1
    ret = "from {} as T1".format(schema["table_names_original"][start])
    try:
        for end in candidate_tables[1:]:
            start_idx += 1    # TODO
            if end in table_alias_dict:
                continue
            path = find_shortest_path(start, end, graph)  # 找到这两个表有没有外键链接（TODO 这里找多了）

            # ************************
            # min_len = 1000
            # for start in candidate_tables[:start_idx]:
            #   path = find_shortest_path(start, end, graph)
            #   if path:
            #     path_len = len(path)
            #   else:
            #     path_len = 0
            #   if path_len < min_len:
            #     min_len = path_len
            #     min_start = start
            # prev_table = min_start
            # ************************

            prev_table = start  # TODO
            if not path:
                table_alias_dict[end] = idx
                idx += 1
                ret = "{} join {} as T{}".format(ret, schema["table_names_original"][end],
                                                 table_alias_dict[end],
                                                 )
                continue
            for node, (acol, bcol) in path:
                if node in table_alias_dict:  # TODO 一定要选择所有的路径吗？不在candidate表里的路径也能选吗？
                # if node in table_alias_dict or node not in candidate_tables:
                    prev_table = node
                    continue
                table_alias_dict[node] = idx
                idx += 1
                ret = "{} join {} as T{} on T{}.{} = T{}.{}".format(ret, schema["table_names_original"][node],
                                                                    table_alias_dict[node],
                                                                    table_alias_dict[prev_table],
                                                                    schema["column_names_original"][acol][1],
                                                                    table_alias_dict[node],
                                                                    schema["column_names_original"][bcol][1])
                prev_table = node
    except:
        traceback.print_exc()
        print("db:{}".format(schema["db_id"]))
        return table_alias_dict, ret
    return table_alias_dict, ret


def normalize_space(format_sql):
  format_sql_1 = [' '.join(sub_sql.strip().replace(',',' , ').replace('(',' ( ').replace(')',' ) ').split()) 
                    for sub_sql in format_sql.split('\n')]
  format_sql_1 = '\n'.join(format_sql_1)
  format_sql_2 = format_sql_1.replace('\njoin',' join').replace(',\n',', ').replace(' where','\nwhere').replace(' intersect', '\nintersect').replace('union ', 'union\n').replace('\nand',' and').replace('order by t2 .\nstart desc', 'order by t2 . start desc')
  return format_sql_2


def get_candidate_tables(format_sql, schema):
  candidate_tables = []

  tokens = format_sql.split()
  for ii, token in enumerate(tokens):
    if '.' in token:
      table_name = token.split('.')[0]
      candidate_tables.append(table_name)

  candidate_tables = list(set(candidate_tables))  # TODO 这里有问题，去重的同时随机了列表顺序
  # *********************** TODO
  # temp_ls = []
  # for k in candidate_tables:
  #   if k not in temp_ls:
  #     temp_ls.append(k)
  # candidate_tables = temp_ls
  # ***********************

  table_names_original = [table_name.lower() for table_name in schema['table_names_original']]
  candidate_tables_id = [table_names_original.index(table_name) for table_name in candidate_tables]

  assert -1 not in candidate_tables_id
  table_names_original = schema['table_names_original']

  return candidate_tables_id, table_names_original


def get_surface_form_orig(format_sql_2, schema):
  column_names_surface_form = []
  column_names_surface_form_original = []
  
  column_names_original = schema['column_names_original']
  table_names_original = schema['table_names_original']
  for i, (table_id, column_name) in enumerate(column_names_original):
    if table_id >= 0:
      table_name = table_names_original[table_id]
      column_name_surface_form = '{}.{}'.format(table_name,column_name)
    else:
      # this is just *
      column_name_surface_form = column_name
    column_names_surface_form.append(column_name_surface_form.lower())
    column_names_surface_form_original.append(column_name_surface_form)
  
  # also add table_name.*
  for table_name in table_names_original:
    column_names_surface_form.append('{}.*'.format(table_name.lower()))
    column_names_surface_form_original.append('{}.*'.format(table_name))

  assert len(column_names_surface_form) == len(column_names_surface_form_original)
  for surface_form, surface_form_original in zip(column_names_surface_form, column_names_surface_form_original):
    format_sql_2 = format_sql_2.replace(surface_form, surface_form_original)

  return format_sql_2


def add_from_clase(sub_sql, from_clause):
  select_right_sub_sql = []
  left_sub_sql = []
  left = True
  num_left_parathesis = 0  # in select_right_sub_sql
  num_right_parathesis = 0 # in select_right_sub_sql
  tokens = sub_sql.split()
  for ii, token in enumerate(tokens):
    if token == 'select':
      left = False
    if left:
      left_sub_sql.append(token)
      continue
    select_right_sub_sql.append(token)
    if token == '(':
      num_left_parathesis += 1
    elif token == ')':
      num_right_parathesis += 1

  def remove_missing_tables_from_select(select_statement):
    tokens = select_statement.split(',')

    stop_idx = -1
    for i in range(len(tokens)):
      idx = len(tokens) - 1 - i
      token = tokens[idx]
      if '.*' in token and 'count ' not in token:
        pass
      else:
        stop_idx = idx+1
        break

    if stop_idx > 0:
      new_select_statement = ','.join(tokens[:stop_idx]).strip()
    else:
      new_select_statement = select_statement

    return new_select_statement

  if num_left_parathesis == num_right_parathesis or num_left_parathesis > num_right_parathesis:
    sub_sqls = []
    sub_sqls.append(remove_missing_tables_from_select(sub_sql))
    sub_sqls.append(from_clause)
  else:
    assert num_left_parathesis < num_right_parathesis
    select_sub_sql = []
    right_sub_sql = []
    for i in range(len(select_right_sub_sql)):
      token_idx = len(select_right_sub_sql)-1-i
      token = select_right_sub_sql[token_idx]
      if token == ')':
        num_right_parathesis -= 1
      if num_right_parathesis == num_left_parathesis:
        select_sub_sql = select_right_sub_sql[:token_idx]
        right_sub_sql = select_right_sub_sql[token_idx:]
        break

    sub_sqls = []
    
    if len(left_sub_sql) > 0:
      sub_sqls.append(' '.join(left_sub_sql))
    if len(select_sub_sql) > 0:
      new_select_statement = remove_missing_tables_from_select(' '.join(select_sub_sql))
      sub_sqls.append(new_select_statement)

    sub_sqls.append(from_clause)
    
    if len(right_sub_sql) > 0:
      sub_sqls.append(' '.join(right_sub_sql))

  return sub_sqls


def postprocess_single(format_sql_2, schema, start_alias_id=0):
  # 找到sql中对应的表，candidate_tables_id存放sql中包含的表在table_names_original列表中的下标
  # TODO 但是为什么下标的顺序不是在sql中表出现的顺序一致呢？
  # TODO candidate_tables_id：[1, 0, 2] 多join了表 / [2, 0, 1] 没join多
  candidate_tables_id, table_names_original = get_candidate_tables(format_sql_2, schema)
  # TODO 没发现有啥改变
  format_sql_2 = get_surface_form_orig(format_sql_2, schema)

  if len(candidate_tables_id) == 0:
    final_sql = format_sql_2.replace('\n', ' ')
  elif len(candidate_tables_id) == 1:
    # easy case
    table_name = table_names_original[candidate_tables_id[0]]
    from_clause = 'from {}'.format(table_name)
    format_sql_3 = []
    for sub_sql in format_sql_2.split('\n'):
      if 'select' in sub_sql:
        format_sql_3 += add_from_clase(sub_sql, from_clause)
      else:
        format_sql_3.append(sub_sql)
    final_sql = ' '.join(format_sql_3).replace('{}.'.format(table_name), '')
  else:
    # more than 1 candidate_tables
    # table_alias_dict：建立一个映射字典，按照table_names_original的下标为键，然后值的数字代表T1 / T2 / T3 / T4这样
    # ret：返回的sql处理结果
    table_alias_dict, ret = gen_from(candidate_tables_id, schema)

    from_clause = ret
    for i in range(len(table_alias_dict)):
      from_clause = from_clause.replace('T{}'.format(i+1), 'T{}'.format(i+1+start_alias_id))

    table_name_to_alias = {}
    for table_id, alias_id in table_alias_dict.items():
      table_name = table_names_original[table_id]
      alias = 'T{}'.format(alias_id+start_alias_id)
      table_name_to_alias[table_name] = alias
    start_alias_id = start_alias_id + len(table_alias_dict)

    format_sql_3 = []
    for sub_sql in format_sql_2.split('\n'):
      if 'select' in sub_sql:
        format_sql_3 += add_from_clase(sub_sql, from_clause)
      else:
        format_sql_3.append(sub_sql)
    format_sql_3 = ' '.join(format_sql_3)

    table_name_to_alias = dict(sorted(table_name_to_alias.items(), key=lambda x: -len(x[0])))
    for table_name, alias in table_name_to_alias.items():
      format_sql_3 = format_sql_3.replace('{}.'.format(table_name), '{}.'.format(alias))

    final_sql = format_sql_3

  for i in range(5):
    final_sql = final_sql.replace('select count ( T{}.* ) '.format(i), 'select count ( * ) ')
    final_sql = final_sql.replace('count ( T{}.* ) from '.format(i), 'count ( * ) from ')
    final_sql = final_sql.replace('order by count ( T{}.* ) '.format(i), 'order by count ( * ) ')
    final_sql = final_sql.replace('having count ( T{}.* ) '.format(i), 'having count ( * ) ')

  return final_sql, start_alias_id


def postprocess_nested(format_sql_2, schema):
  candidate_tables_id, table_names_original = get_candidate_tables(format_sql_2, schema)
  if len(candidate_tables_id) == 1:
    format_sql_2 = get_surface_form_orig(format_sql_2, schema)
    # easy case
    table_name = table_names_original[candidate_tables_id[0]]
    from_clause = 'from {}'.format(table_name)
    format_sql_3 = []
    for sub_sql in format_sql_2.split('\n'):
      if 'select' in sub_sql:
        format_sql_3 += add_from_clase(sub_sql, from_clause)
      else:
        format_sql_3.append(sub_sql)
    final_sql = ' '.join(format_sql_3).replace('{}.'.format(table_name), '')
  else:
    # case 1: easy case, except / union / intersect
    # case 2: nested queries in condition
    final_sql = []

    num_keywords = format_sql_2.count('except') + format_sql_2.count('union') + format_sql_2.count('intersect')
    num_select = format_sql_2.count('select')

    def postprocess_subquery(sub_query_one, schema, start_alias_id_1):
      num_select = sub_query_one.count('select ')
      final_sub_sql = []
      sub_query = []
      for sub_sql in sub_query_one.split('\n'):
        if 'select' in sub_sql:
          if len(sub_query) > 0:
            sub_query = '\n'.join(sub_query)
            sub_query, start_alias_id_1 = postprocess_single(sub_query, schema, start_alias_id_1)
            final_sub_sql.append(sub_query)
            sub_query = []
          sub_query.append(sub_sql)
        else:
          sub_query.append(sub_sql)
      if len(sub_query) > 0:
        sub_query = '\n'.join(sub_query)
        sub_query, start_alias_id_1 = postprocess_single(sub_query, schema, start_alias_id_1)
        final_sub_sql.append(sub_query)

      final_sub_sql = ' '.join(final_sub_sql)
      return final_sub_sql, False, start_alias_id_1

    start_alias_id = 0
    sub_query = []
    for sub_sql in format_sql_2.split('\n'):
      if 'except' in sub_sql or 'union' in sub_sql or 'intersect' in sub_sql:
        sub_query = '\n'.join(sub_query)
        sub_query, _, start_alias_id = postprocess_subquery(sub_query, schema, start_alias_id)
        final_sql.append(sub_query)
        final_sql.append(sub_sql)
        sub_query = []
      else:
        sub_query.append(sub_sql)
    if len(sub_query) > 0:
      sub_query = '\n'.join(sub_query)
      sub_query, _, start_alias_id = postprocess_subquery(sub_query, schema, start_alias_id)
      final_sql.append(sub_query)
    
    final_sql = ' '.join(final_sql)

  # special case of from a subquery
  final_sql = final_sql.replace('select count ( * ) (', 'select count ( * ) from (')

  return final_sql


def postprocess_one(pred_sql, schema):
  # 把伪sql中的group_by / order_by / limit_value / value / distinct 进行替换
  pred_sql = pred_sql.replace('group_by', 'group by').replace('order_by', 'order by').replace('limit_value', 'limit 1').replace('_EOS', '').replace(' value ',' 1 ').replace('distinct', '').strip(',').strip()
  # 只替换了有两个空格的sql中间的value，没替换末尾的value
  if pred_sql.endswith('value'):
    pred_sql = pred_sql[:-len('value')] + '1'

  try:
    # 给where前面把空格换成了\n，而且不仅仅是where，貌似distinct/union/intersect/join等都会加
    # TODO 不知道有什么用
    format_sql = sqlparse.format(pred_sql, reindent=True)
  except:
    # TODO 不知道有什么用
    return pred_sql
  format_sql_2 = normalize_space(format_sql)

  # 计算有几个select
  num_select = format_sql_2.count('select')

  # 得到最后的sql
  if num_select > 1:
    final_sql = postprocess_nested(format_sql_2, schema)
  else:
    final_sql, _ = postprocess_single(format_sql_2, schema)

  return final_sql


def postprocess(predictions, database_schema, remove_from=False):
  correct = 0
  total = 0
  postprocess_sqls = {}

  # 在预测的文件中，每一行都是一个json对象
  for pred in predictions:
    db_id = pred['database_id']             # db的名字
    schema = database_schema[db_id]         # 对应db的schema
    if db_id not in postprocess_sqls:       # 按照db分类建立字典信息
      postprocess_sqls[db_id] = []

    interaction_id = pred['interaction_id'] # 相应的db的第几号session
    turn_id = pred['index_in_interaction']  # 相应的session第几轮
    total += 1                              # （感觉没用）总的pred数量

    pred_sql_str = ' '.join(pred['flat_prediction'])      # 把pred列表变成字符串，如'select 比赛.名称 where 比赛.举办单位 = value'

    gold_sql_str = ' '.join(pred['flat_gold_queries'][0]) # 把gold列表变成字符串，如'select 比赛.名称 where 比赛.举办单位 = value'
    if pred_sql_str == gold_sql_str:        # （感觉没用）总的正确数量，不能这么简单暴力地相等吧
      correct += 1                          # 实测了一下，这里认为正确的是973，但是实际正确的是1012

    postprocess_sql = pred_sql_str
    if remove_from:
      # if db_id == "购书平台" and interaction_id == "3" and turn_id == 1:
        # print("********************************************")
      try:  # TODO 这里可能有解析不出来的sql，主要是预测错了表
        postprocess_sql = postprocess_one(pred_sql_str, schema) # 对伪SQL进行后处理
      except:
        postprocess_sql = "wrong sql"

      # 有一条sql语句会在评测部分评测错，这里保存一下output.txt
      # temp_sql = "select T1.国家 from 台风影响的国家 as T1 join 台风 as T2 on T1.台风id = T2.台风id where T2.名称 = ( select T3.名称 from 台风 as T3 join 台风影响的中国省份 as T4 on T3.台风id = T4.台风id where T4.省份 = 1 )"
      # if postprocess_sql == temp_sql:
      #   print("********************************************")

      # 购书平台/3的第二轮，也就是index_in_interaction为1的会有问题
      # if db_id == "购书平台" and interaction_id == "3" and turn_id == 1:
        # 偶尔这个postprocess_sql会多join一个表格，"电子书"
        # print("********************************************")
        # print(postprocess_sql)
        # print("********************************************")

    postprocess_sqls[db_id].append((postprocess_sql, interaction_id, turn_id))

  # print (correct, total, float(correct)/total)
  return postprocess_sqls


def read_prediction(pred_file):
  print('Read prediction from', pred_file)
  predictions = []
  with open(pred_file, encoding="utf-8") as f:
    for line in f:
      pred = json.loads(line)
      predictions.append(pred)
  print('Number of predictions', len(predictions))
  return predictions

def read_schema(table_schema_path):
  with open(table_schema_path, encoding="utf-8") as f:
    database_schema = json.load(f)

  database_schema_dict = {}
  for table_schema in database_schema:
    db_id = table_schema['db_id']
    database_schema_dict[db_id] = table_schema

  return database_schema_dict

def write_and_evaluate(postprocess_sqls, db_path, table_schema_path, gold_path, dataset):
  db_list = []
  with open(gold_path, encoding="utf-8") as f:
    for line in f:
      line_split = line.strip().split('\t')
      if len(line_split) != 2:
        continue
      db = line.strip().split('\t')[1]
      if db not in db_list:
        db_list.append(db)

  output_file = 'output_temp.txt'
  if dataset == 'spider':
    with open(output_file, "w", encoding="utf-8") as f:
      for db in db_list:
        for postprocess_sql, interaction_id, turn_id in postprocess_sqls[db]:
          f.write(postprocess_sql+'\n')

    command = 'python3 eval_scripts/evaluation.py --db {} --table {} --etype match --gold {} --pred {}'.format(db_path,
                                                                                                  table_schema_path,
                                                                                                  gold_path,
                                                                                                  os.path.abspath(output_file))
  elif dataset in ['sparc', 'cosql', 'chase', 'SeSQL']:
    cnt = 0
    with open(output_file, "w", encoding="utf-8") as f:
      for db in db_list:
        for postprocess_sql, interaction_id, turn_id in postprocess_sqls[db]:
          if turn_id == 0 and cnt > 0:
            f.write('\n')
          f.write('{}\n'.format(postprocess_sql))
          cnt += 1
      f.write('\n')

    command = 'python eval_scripts/evaluation_sqa.py --db {} --table {} --etype match --gold {} --pred {}'.format(db_path,
                                                                                                      table_schema_path,
                                                                                                      gold_path,
                                                                                                      os.path.abspath(output_file))
  command += '; rm output_temp.txt'
  return command

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dataset', choices=('spider', 'sparc', 'cosql', 'chase', 'SeSQL'), default='SeSQL')
  parser.add_argument('--split', type=str, default='test')
  parser.add_argument('--pred_file', type=str, default='logs_SeSQL_editsql/test_use_predicted_queries_predictions.json')
  parser.add_argument('--remove_from', action='store_true', default=True)
  args = parser.parse_args()

  db_path = 'data/database/'
  if args.dataset == 'spider':
    table_schema_path = 'data/spider/tables.json'
    if args.split == 'dev':
      gold_path = 'data/spider/dev_gold.sql'
  elif args.dataset == 'sparc':
    table_schema_path = 'data/sparc/tables.json'
    if args.split == 'dev':
      gold_path = 'data/sparc/dev_gold.txt'
  elif args.dataset == 'cosql':
    table_schema_path = 'data/cosql/tables.json'
    if args.split == 'dev':
      gold_path = 'data/cosql/dev_gold.txt'
  elif args.dataset == 'chase':
    db_path = '../data/database_cn'
    table_schema_path = 'data/chase/tables.json'
    if args.split == 'dev':
      gold_path = 'data/chase/dev_gold.txt'
  elif args.dataset == 'SeSQL':
    db_path = '../data/database_cn'
    table_schema_path = 'data/SeSQL/tables.json'
    if 'dev' in args.split:
      gold_path = 'data/SeSQL/dev_gold.txt'
    if 'test' in args.split:
      gold_path = 'data/SeSQL/test_gold.txt'


  pred_file = args.pred_file  # 'logs_chase_editsql/valid_use_predicted_queries_predictions.json'

  database_schema = read_schema(table_schema_path)  # 其实就是tables.json的内容
  predictions = read_prediction(pred_file)          # 把模型的预测文件读入
  # 这里就是一个后处理过程了，把伪SQL处理成正常的SQL
  # 处理出来的东西，会由一个有3个元素的元组构成，其含义为：
  #   postprocess_sql：后处理过的SQL
  #   interaction_id：是那个session
  #   turn_id：第几轮
  postprocess_sqls = postprocess(predictions, database_schema, args.remove_from)  

  command = write_and_evaluate(postprocess_sqls, db_path, table_schema_path, gold_path, args.dataset)

  eval_output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
  with open(pred_file+'.eval', 'w', encoding="utf-8") as f:
    f.write(eval_output.decode("utf-8"))
  print('Eval result in', pred_file+'.eval')
