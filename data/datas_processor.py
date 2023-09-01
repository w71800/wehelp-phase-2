import copy
import mysql.connector as connector
db = connector.connect(
  host="localhost",
  user="root",
  password="0000",
  database="wehelp"
)

cursor = db.cursor()
# [{page, data}, {page, data}]
def folding_data(src_container, length = 12):
	page_count = 0
	data_count = 0
	temporary_container = copy.deepcopy(src_container)
	data_container = []
	single_page = {
		"page": page_count,
		"data": []
	}

	for i, data in enumerate(temporary_container):
		if data_count < length:
			single_page["data"].append(data)
			data_count += 1

		if data_count == length:
			data_container.append(single_page)
			page_count += 1
			single_page = {
				"page": page_count,
				"data": []
			}
			data_count = 0
		
		if i + 1 == len(temporary_container):
			data_container.append(single_page)
	else:
		return data_container

import json, re, sys
sys.path.append("modules")
data_resorts = []
data_mrts = []
with open('taipei-attractions.json', 'r') as file:
  data_raw = json.load(file)["result"]["results"]
  pattern = r"https?://\S+?\.[jJpP].."
  page_count = 0
  data_count = 0
  for i, item in enumerate(data_raw):
    dict_data = {
      "id": i + 1,
      "name": item["name"],
      "category": item["CAT"],
      "description": item["description"],
      "address": item["address"],
      "transport": item["direction"],
      "mrt": item["MRT"] if item["MRT"] is not None else "empty",
      "lat": item["latitude"],
      "lng": item["longitude"],
      "images": re.findall(pattern, item["file"]),
      "page": None
    }

    if data_count < 12:
      dict_data["page"] = page_count
      data_count += 1
    if data_count == 12:
      data_count = 0
      page_count += 1
    
    data_resorts.append(dict_data) 
    

# print(data_resorts)
    

# 抽出捷運站資料，並用一個列表裝載周圍景點
# 目標：
# [
#   { "mrt": "劍潭", "resorts": [.....] },
# ]
# dict_template = {}
# for resort in data_resorts:
#   name = resort["name"]
#   mrt = resort["mrt"]

#   if mrt not in dict_template:
#     dict_template[mrt] = []
    
#   dict_template[mrt].append(name)
# else:
#   data_mrts = [ { "mrt": mrt, "resorts": resorts } for mrt, resorts in dict_template.items() ]

# for i, item in enumerate(data_mrts):
#   item["id"] = i + 1


def show_json(data):
  with open('test.json', 'w', encoding="utf-8") as file:
    file.write("[")
    for i, item in enumerate(data):
      print(item)
      # json.dump(item, file, ensure_ascii=False)
      json.dump(item, file, ensure_ascii=False)
      if i < len(data) - 1:
        file.write(",")
    file.write("]")

# show_json(data_mrts)
show_json(data_resorts)

for resort in data_resorts:
  sql = "INSERT into resorts(id, name, category, description, address, transport, mrt, lat, lng, images, page) " \
        "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  
  value = (resort["id"], resort["name"], resort["category"], resort["description"], resort["address"], resort["transport"], resort["mrt"], resort["lat"], resort["lng"], json.dumps(resort["images"]), resort["page"])

  cursor.execute(sql, value)
else:
  db.commit()






  


  

