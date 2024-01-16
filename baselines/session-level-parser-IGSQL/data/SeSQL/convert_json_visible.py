import json

file_names = ["tables.json", "test.json"]
for name in file_names:
    with open(name, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    with open(name, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False)