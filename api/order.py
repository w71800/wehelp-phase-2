from utils.utils import reform_attraction, get_token, check_auth
from models import connectToDB, connector, connectToTP
from flask import Blueprint, request, make_response, jsonify
import datetime
import json

order_blueprint = Blueprint("order", __name__)

@order_blueprint.route("/api/order", methods=["POST"])
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