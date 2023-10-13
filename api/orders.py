from api import *

orders_blueprint = Blueprint("orders", __name__)

@orders_blueprint.route("/api/orders")
def api_orders():
	is_auth = check_auth(get_token())
	if not is_auth:
		response = {
  			"error": True,
  			"message": "Not signin."
			}
		return make_response(jsonify(response), 403)
	
	user_id = is_auth["id"]
	
	with connectToDB() as (db, cursor):
		try:
			sql = """
						SELECT id, number, price, trips, payment 
						from orders WHERE member_id = (%s)
						"""
			cursor.execute(sql, (user_id, ))
			orders = cursor.fetchall()

			data = []
			for order in orders:
				id, number, price, trips, payment = order
				dict = {
					"id": id,
					"number": number,
					"price": price,
					"trips": json.loads(trips),
					"payment": payment,
				}

				data.append(dict)

			response = { "data": data }
			return make_response(jsonify(response), 200)
		except connector.Error as e:
			response = {
  				"error": True,
  				"message": str(e)
				}
			return make_response(jsonify(response), 400)

		

	
