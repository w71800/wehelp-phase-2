import json
import jwt
import datetime
from contextlib import contextmanager
from flask import *

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

import mysql.connector as connector
dbconfig = {
	"host": "localhost",
	"user": "root",
	"password": "0000",
	"database": "wehelp",
	"pool_name": "pool",
	"pool_size": 5
}
# 建立一個 pool
connection_pool = connector.pooling.MySQLConnectionPool(**dbconfig)


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

@contextmanager
def connectToDB():
	cursor = None
	db = None
	try:
		db = connection_pool.get_connection()
		cursor = db.cursor()

		yield db, cursor
	finally:
		if cursor:
			cursor.close()
		if db:
			db.close()

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
	db = connection_pool.get_connection()
	cursor = db.cursor()

	page = int(request.args.get("page")) if request.args.get("page") else None
	keyword = request.args.get("keyword")

	if page == None:
		response = {
			"error": True, 
			"message": "未輸入頁數"
		}
		db.close()
		cursor.close()

		return make_response(jsonify(response), 400)

	try:
		response = None
		if keyword is None:
			sql = "SELECT * from resorts LIMIT 13 OFFSET %s"
			value = (12 * page, )
		else:
			sql = "SELECT * FROM resorts WHERE name LIKE (%s) or mrt = (%s) LIMIT 13 OFFSET %s"
			value = ('%' + keyword + '%', keyword, 12 * page, )

		cursor.execute(sql, value)
		result = cursor.fetchall()
		if len(result) == 0:
			response = {
				"error": True, 
				"message": "No matched datas have been found"
			}
			db.close()
			cursor.close()
			return make_response(jsonify(response), 500)
		
		data_container = []
		next_container = []
		for index, item in enumerate(result):
			dict = reform_attraction(item)
			if index < 12:
				data_container.append(dict)
			else:
				next_container.append(dict)
			
		else:
			next_page = None if len(next_container) == 0 else page + 1
			response = {
				"nextPage": next_page,
				"data": data_container
			}
		db.close()
		cursor.close()
		return make_response(jsonify(response), 200)
		
	except connector.Error as e:
		response = {
			"error": True, 
			"message": f"伺服器發生內部錯誤：{e}"
			}
		print(e)
		db.close()
		cursor.close()
		return make_response(jsonify(response), 500)
	
# 選取 id 的模式
@app.route("/api/attraction/<attractionId>")
def api_attraction＿id(attractionId):
	db = connection_pool.get_connection()
	cursor = db.cursor()

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
			db.close()
			cursor.close()
			return make_response(jsonify(response), 400)
		
		else:
			response = {
				"data": reform_attraction(result[0])
			}
			db.close()
			cursor.close()
			return make_response(jsonify(response), 200)
		
	except Exception as e:
		response = { 
			"error": True, 
			"message": f"伺服器發生內部錯誤：{e}"
		}
		print(e)
		db.close()
		cursor.close()
		return make_response(jsonify(response), 500)

# 抓出所有 MRT 的資料，並按照景點數量由大到小排序
@app.route("/api/mrts")
def api_mrts():
	db = connection_pool.get_connection()
	cursor = db.cursor()
	response = None

	try:
		sql = "SELECT mrt, count(name) from resorts GROUP BY mrt ORDER BY count(name) DESC"
		cursor.execute(sql)
		result = cursor.fetchall()

		result_container = [ item[0] for item in result ]
		result_container = list(filter(lambda x : x != "empty", result_container))
		response = {
			"data": result_container
		}
		db.close()
		cursor.close()
		return make_response(jsonify(response), 200)
	
	except connector.Error as e:
		response = {
				"error": True, 
				"message": f"伺服器發生內部錯誤：{e}"
				}
		db.close()
		cursor.close()
		return make_response(jsonify(response), 500)

# 註冊會員
@app.route("/api/user", methods=["POST"])
def api_user():
	name, email, password = request.form.values()
	with connectToDB() as (db, cursor):
		try:
			sql = "INSERT into members(name, email, password) values(%s, %s, %s)"
			values = (name, email, password, )
			cursor.execute(sql, values)
			
			db.commit()
			
			response = { "ok": True }
			return make_response(jsonify(response), 200)
		
		except connector.Error as e:
			error_code = e.errno
			error_msg = str(e)

			http_code = 400 if error_code == 1062 else 500

			response = { "error": True, "message": error_msg }
			return make_response(jsonify(response), http_code)

# 會員登入或抓到登入狀態
@app.route("/api/auth", methods=["GET", "PUT"])
def api_auth():
	method = request.method
	key = "secret"
	if(method == "GET"):
		auth_header = request.headers.get("Authorization")
		
		if not auth_header:
			response = { "data": None }
			return make_response(jsonify(response), 200)
		
		token = auth_header.split()[1]
		try:
			result = jwt.decode(token, key, algorithms=["HS256"])
			data = result.get("data")
			response = { "data": data }
		
		except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
			response = { "data": None }

		return make_response(jsonify(response), 200)


	else:
		# 抓到是否有對應的 email 和 password 是否正確
		email, password = request.form.values()

		with connectToDB() as (db, cursor):
			try:
				sql = "SELECT id, email, name from members where email = (%s) and password = (%s)"
				values = (email, password, )
				cursor.execute(sql, values)
				result = cursor.fetchall()

				if len(result) == 0:
					response = { "error": True, "message": "This email is not signed or the password is wrong." }
					return make_response(jsonify(response), 400)
				
				id, email, name = result[0]
				data = {
					"id": id,
					"email": email,
					"name": name
				}

				exp_time = datetime.datetime.utcnow() + datetime.timedelta(days = 7)
				encoded = jwt.encode({
					"data": data,
					"exp": exp_time
				}, key, algorithm = "HS256")

				response = { "token": encoded }
				return make_response(jsonify(response), 200)

			except connector.Error as e:
				error_msg = str(e)

				response = { "error": True, "message": error_msg }
				return make_response(jsonify(response), 500)
	

app.run(host="0.0.0.0", port=3000, debug=True)