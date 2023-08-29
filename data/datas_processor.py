import mysql.connector as connector
db = connector.connect(
  host="localhost",
  user="root",
  password="0000",
  database="wehelp"
)

cursor = db.cursor()

import json, re
data_resorts = []
data_mrts = []
with open('taipei-attractions.json', 'r') as file:
  data_raw = json.load(file)["result"]["results"]
  pattern = r"https?://\S+?\.[jJpP].."

  for item in data_raw:
    dict_data = {
      "id": item["_id"],
      "name": item["name"],
      "category": item["CAT"],
      "description": item["description"],
      "address": item["address"],
      "transport": item["direction"],
      "mrt": item["MRT"] if item["MRT"] is not None else "empty",
      "lat": item["latitude"],
      "lng": item["longitude"],
      "images": re.findall(pattern, item["file"]),
    } 
    
    data_resorts.append(dict_data)

# 抽出捷運站資料，並用一個列表裝載周圍景點
# 目標：
# [
#   { "mrt": "劍潭", "resorts": [.....] },
# ]
dict_template = {}
for resort in data_resorts:
  name = resort["name"]
  mrt = resort["mrt"]

  if mrt not in dict_template:
    dict_template[mrt] = []
    
  dict_template[mrt].append(name)
else:
  data_mrts = [ { "mrt": mrt, "resorts": resorts } for mrt, resorts in dict_template.items() ]

for i, item in enumerate(data_mrts):
  item["id"] = i + 1

# 加上 mrt_id
for resort in data_resorts:
  for mrt in data_mrts:
    if resort["mrt"] == mrt["mrt"]:
      resort["mrt_id"] = mrt["id"]
  resort.pop("mrt")

def show_json(data):
  with open('test.json', 'w', encoding="utf-8") as file:
    file.write("[")
    for i, item in enumerate(data):
      json.dump(item, file, ensure_ascii=False)
      if i < len(data) - 1:
        file.write(",")
    file.write("]")

# show_json(data_mrts)
show_json(data_resorts)

for resort in data_resorts:
  sql = "INSERT into resorts(id, name, category, description, address, transport, mrt_id, lat, lng, images) " \
        "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  
  value = (resort["id"], resort["name"], resort["category"], resort["description"], resort["address"], resort["transport"], resort["mrt_id"], resort["lat"], resort["lng"], json.dumps(resort["images"]),)

  cursor.execute(sql, value)
else:
  db.commit()

# for mrt in data_mrts:
#   sql = "INSERT into mrts(id, name) value(%s, %s)"
#   value = (mrt["id"], mrt["mrt"])

#   cursor.execute(sql, value)
# else:
#   db.commit()





  


  

