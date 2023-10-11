import json

def show_json(data):
  with open('test.json', 'w', encoding="utf-8") as file:
    file.write("[")
    for i, item in enumerate(data):
      json.dump(item, file, ensure_ascii=False)
      if i < len(data) - 1:
        file.write(",")
    file.write("]")