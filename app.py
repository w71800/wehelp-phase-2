import json
import jwt
import datetime
from contextlib import contextmanager
from flask import *
import requests

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

# 取得 Token
def get_token():
	auth_header = request.headers.get("Authorization")

	# print(auth_header)
	if not auth_header or auth_header == "undefined":
		token = None
	else:
		token = auth_header.split()[1]	
	
	return token

def check_auth(token, key="secret"):
	if not token or token == "undefined":
		return False
	else:
		user = jwt.decode(token, key, algorithms=["HS256"])["data"]
		return user

def connectToTP(order):
	prime = order["prime"]
	order = order["order"]
	contact = order["contact"]
	TP_url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
	data = {
		"prime": prime,
		"partner_key": "partner_rD3NG5KHlV7RbYLzLbKuEQjLhcrVXxcL0lJCfYRDLtQzvH1FNba3j6gg",
		"merchant_id": "w71800_CTBC",
		"details":"台北一日遊",
		"amount": order["price"],
		"cardholder": {
				"phone_number": contact["phone"],
				"name": contact["name"],
				"email": contact["email"]
  	}
	}
	headers = {
		"Content-Type": "application/json",
		"x-api-key": "partner_rD3NG5KHlV7RbYLzLbKuEQjLhcrVXxcL0lJCfYRDLtQzvH1FNba3j6gg"
	}
	response = requests.post(TP_url, data = json.dumps(data), headers = headers)
	
	return response
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
@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")

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
		sql = "select MAX(id) from members"
		cursor.execute(sql)
		max_id = cursor.fetchall()[0][0]

		try:
			sql = "INSERT into members(id, name, email, password) values(%s, %s, %s, %s)"
			values = (max_id + 1, name, email, password, )
			cursor.execute(sql, values)
		
		except connector.Error as e:
			error_code = e.errno
			error_msg = str(e)
			
			db.rollback()

			http_code = 400 if error_code == 1062 else 500

			response = { "error": True, "message": error_msg }
			return make_response(jsonify(response), http_code)
		else:
			db.commit()

			response = { "ok": True }
			return make_response(jsonify(response), 200)

# 會員登入或抓到登入狀態
@app.route("/api/auth", methods=["GET", "PUT"])
def api_auth():
	method = request.method
	key = "secret"
	if(method == "GET"):
		token = get_token()
		
		if not token:
			response = { "data": None }
			return make_response(jsonify(response), 200)
		
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
		print(request.form.values())

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
	
@app.route("/api/booking", methods=["GET", "POST", "DELETE"])
def api_booking():
	method = request.method

	is_auth = check_auth(get_token())
	if not is_auth:
		response = {
  			"error": True,
  			"message": "Not signin."
			}
		return make_response(jsonify(response), 403)
	else:
		user_id = is_auth["id"]
		
	if method == "GET":
		with connectToDB() as (db, cursor):
			try:
				sql = """
							SELECT resorts.id, resorts.name, resorts.address, resorts.images, date, time, price
							FROM bookings 
							LEFT JOIN resorts ON resorts.id = bookings.resort_id
							WHERE bookings.member_id = (%s);
							"""
				cursor.execute(sql, (user_id, ))
				result = cursor.fetchall()

				if len(result) == 0:
					response = { "data": None }
					return make_response(jsonify(response))

				bookings = []
				for item in result:
					attraction_id, attraction_name, attraction_address, attraction_images, date, time, price = item
					data = {
						"attraction": {
							"id": attraction_id,
							"name": attraction_name,
							"address": attraction_address,
							"image": json.loads(attraction_images)
						},
						"date": date,
						"time": time,
						"price": price
					}
					bookings.append({ "data": data })
				else:
					return make_response(jsonify(bookings))
			except connector.Error as e:
				response = {
					"error": True,
					"message": str(e)
				}
				return make_response(jsonify(response), 500)

	if method == "POST":
		data = request.form.values()
		attraction_id, date, time, price = data
		with connectToDB() as (db, cursor):
			try:
				# 先檢查是否有同樣的 resort_id
				sql = """
							SELECT member_id, resort_id from bookings
							WHERE member_id = (%s) and resort_id = (%s)
							"""
				value = (user_id, attraction_id)
				cursor.execute(sql, value)

				result = cursor.fetchall()
				if len(result) != 0:
					response = {
						"error": True,
						"message": "This booking is duplicated"
					}
					return make_response(jsonify(response), 400)
				
				sql = """
							INSERT into bookings(member_id, resort_id, date, time, price)
							VALUES(%s, %s, %s, %s, %s)
							"""
				value = (user_id, attraction_id, date, time, price, )
				cursor.execute(sql, value)
			
				db.commit()

				response = { "ok": True }
				return make_response(jsonify(response))
			except connector.Error as e:
				db.rollback()

				response = {
  				"error": True,
  				"message": str(e)
				}
				return make_response(jsonify(response), 400)
		
	if method == "DELETE":
		with connectToDB() as (db, cursor):
			try:
				resort_id = request.get_json().get("attractionId")
				sql = "DELETE from bookings WHERE member_id = (%s) and resort_id = (%s)"
				cursor.execute(sql, (user_id, resort_id, ))

				db.commit()
				response = { "ok": True }
				return make_response(jsonify(response))
			
			except connector.Error as e:
				response = {
					"error": True,
					"message": str(e)
				}
				return make_response(jsonify(response), 500)

@app.route("/api/order", methods=["POST"])
def api_order():
	number = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	is_auth = check_auth(get_token())
	if not is_auth:
		response = {
  			"error": True,
  			"message": "Not signin."
			}
		return make_response(jsonify(response), 403)
	else:
		user_id = is_auth["id"]

	orderData = request.get_json()
	order = orderData["order"]
	contact = order["contact"]

	# 將訂單放到資料庫中
	with connectToDB() as (db, cursor):
		try:
			sql = """
						INSERT into orders(number, price, member_id, trips, contact, payment)
						VALUES(%s, %s, %s, %s, %s, %s)
						"""
			values = (number, order["price"], user_id, json.dumps(order["trips"]),  json.dumps(contact), 1, )
			cursor.execute(sql, values)

			db.commit()

		except connector.Error as e:
			db.rollback()
			response = { "error": True, "message": str(e) }
			return make_response(jsonify(response), 400)
		
	# 移除掉 bookings 內的內容
	with connectToDB() as (db, cursor):
		try:
			sql = """
						DELETE from bookings WHERE member_id = (%s);
						"""
			cursor.execute(sql, (user_id, ))
			db.commit()

		except connector.Error as e:
			db.rollback()
			response = { "error": True, "message": str(e) }
			return make_response(jsonify(response), 500)
	
	# 開始對 TP Server 做付款請求
	TPresponse = connectToTP(orderData)
	content_json = TPresponse.json()
	if content_json["status"] == 0:
		# 更新 order 的付款狀況
		with connectToDB() as (db, cursor):
			try:
				sql = """
							UPDATE orders SET payment = 0 WHERE number = (%s);
							"""
				cursor.execute(sql, (number, ))
				db.commit()

				data = { 
				"number": number, 
				"payment": {
					"status": 0,
					"message": "付款成功"
				}
			}
				response = { "data": data }
				return make_response(jsonify(response), 200)

			except connector.Error as e:
				db.rollback()
				response = { "error": True, "message": str(e) }
				return make_response(jsonify(response), 500)
		
	else:
		data = {
			"number": number,
			"payment": {
				"status": content_json["status"],
				"message": content_json["msg"]
			}
		}
		response = { "data": data }
		return make_response(jsonify(response), 200)

@app.route("/api/order/<number>")
def api_orderNumber(number):
	data = None
	is_auth = check_auth(get_token())
	if not is_auth:
		response = {
  			"error": True,
  			"message": "Not signin."
			}
		return make_response(jsonify(response), 403)
	else:
		user_id = is_auth["id"]
	with connectToDB() as (db, cursor):
		try:
			sql = """
						SELECT number, price, trips, contact, payment from orders WHERE number = (%s)
						"""
			cursor.execute(sql, (number, ))
			number, price, trips, contact, payment = cursor.fetchall()[0]

			data = {
				"number": number,
				"price": price,
				"trips": json.loads(trips),
				"contact": json.loads(contact),
				"status": payment
			}
			response = { "data": data }
			return make_response(jsonify(response), 200)
		
		except connector.Error as e:
			response = { "error": True, "message": str(e) } 
			return make_response(jsonify(response), 500)
	


app.run(host="0.0.0.0", port=3000, debug=True)