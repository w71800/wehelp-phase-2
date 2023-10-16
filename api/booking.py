from api import *
import json

booking_blueprint = Blueprint("booking", __name__)

@booking_blueprint.route("/api/booking", methods=["GET", "POST", "DELETE"])
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