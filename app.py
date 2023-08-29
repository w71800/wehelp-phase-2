# 暫時可視化 JSON 用
import sys, json
sys.path.append("modules")
import tools

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
	id, name, category, description, address, lat, images, transport, lng, mrt = raw
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
			"images": json.loads(images)
		}

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

# 一口氣取一整包的模式
@app.route("/api/attractions/")
def api_attractions():
	response = None
	sql = "SELECT * from resorts"
	cursor.execute(sql)
	result = cursor.fetchall()

	data_container = []
	for item in result:
		dict = reform_attraction(item)
		data_container.append(dict)
	else:
		response = data_container

	return jsonify(response)


# 選取 id 的模式
@app.route("/api/attractions/<attractionId>")
def api_attraction＿id(attractionId):
	try:
		response = None
		sql = "SELECT * from resorts where id = (%s)"
		cursor.execute(sql, (attractionId, ))
		result = cursor.fetchall()

		if len(result) == 0:
			response = { "error": True, "message": "搜尋的編號所對應之資料不存在" }
			return make_response(jsonify(response), 400)
		else:
			response = reform_attraction(result[0])
			return make_response(jsonify(response), 200)
		
	except Exception as e:
		response = {"error": True, "message": "伺服器發生內部錯誤"}
		return make_response(jsonify(response), 500)


app.run(host="0.0.0.0", port=3000, debug=True)