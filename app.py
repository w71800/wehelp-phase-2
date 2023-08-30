# 暫時可視化 JSON 用
import sys, json, copy

from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
import mysql.connector as connector
db = connector.connect(
	host="localhost",
	user="root",
	password="0000",
	database="wehelp"
)
cursor = db.cursor()

# 放入一個未處理的 row tuple 轉換成 dict
def reform_attraction(raw):
	id, name, category, description, address, lat, images, transport, lng, mrt, page = raw
		
	return {
		"id": id,
		"name": name,
		"category": category,
		"description": description,
		"address": address,
		"transport": transport,
		"mrt": mrt,
		"lat": lat,
		"lng": lng,
		"images": json.loads(images),
	}
# 將原始資料整理成每 12 個一組 [{page, data}, {page, data}]
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
		
# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

##### api 路由 #####

# 一口氣取一整包的模式
@app.route("/api/attractions/")
def api_attractions():
	page = int(request.args.get("page")) if request.args.get("page") else None
	keyword = request.args.get("keyword")

	if page == None:
		response = {
			"error": True, 
			"message": "未輸入頁數"
		}
		return make_response(jsonify(response), 400)

	try:
		response = None
		if keyword is None:
			sql = "SELECT * from resorts LIMIT 12 OFFSET %s"
			value = (12 * page, )
		else:
			sql = "SELECT * FROM resorts WHERE name LIKE (%s) or mrt = (%s) LIMIT 12 OFFSET %s"
			value = ('%' + keyword + '%', keyword, 12 * page, )

		cursor.execute(sql, value)
		result = cursor.fetchall()
		if len(result) == 0:
			response = {
				"error": True, 
				"message": "伺服器發生內部錯誤"
			}
			return make_response(jsonify(response), 500)
		
		data_container = []
		for item in result:
			dict = reform_attraction(item)
			data_container.append(dict)
		else:
			response = {
				"nextPage": page + 1,
				"data": data_container
			}

		return make_response(jsonify(response), 200)
		
	except Exception as e:
		response = {
			"error": True, 
			"message": "伺服器發生內部錯誤"
			}
		print(e)
		return make_response(jsonify(response), 500)

# 選取 id 的模式
@app.route("/api/attraction/<attractionId>")
def api_attraction＿id(attractionId):
	try:
		response = None
		sql = "SELECT * from resorts where id = (%s)"
		cursor.execute(sql, (attractionId, ))
		result = cursor.fetchall()

		if len(result) == 0:
			response = { 
				"error": True, 
				"message": "搜尋的編號所對應之資料不存在" 
			}
			return make_response(jsonify(response), 400)
		
		else:
			response = {
				"data": reform_attraction(result[0], False)
			}
			return make_response(jsonify(response), 200)
		
	except Exception as e:
		response = { 
			"error": True, 
			"message": "伺服器內部出錯"
		}
		return make_response(jsonify(response), 500)

# 抓出所有 MRT 的資料，並按照景點數量由大到小排序
@app.route("/api/mrts")
def api_mrts():
	response = None
	try:
		sql = "SELECT name, mrt from resorts"
		cursor.execute(sql)
		result = cursor.fetchall()

		dict = {}
		for item in result:
			name, mrt = item
			if dict.get(mrt) is None:
				dict[mrt] = []
				dict[mrt].append(name)
			else:
				dict[mrt].append(name)
		else:
			# [{mrt: "", resorts: [...],}]
			list = []
			for mrt, resorts in dict.items():
				if mrt == "empty":
					continue
				list.append({
					"mrt": mrt,
					"resorts": resorts,
					"length": len(resorts)
				})
			else:
				# 根據 resorts 數排序
				list.sort(key = lambda item : len(item["resorts"]), reverse = True)
		
		result_container = [ item["mrt"] for item in list ]
		response = {
			"data": result_container
		}
		return make_response(jsonify(response), 200)
	
	except Exception as e:
		response = {
				"error": True, 
				"message": "伺服器發生內部錯誤"
				}
		return make_response(jsonify(response), 500)
		


app.run(host="0.0.0.0", port=3000, debug=True)