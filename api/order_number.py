from api import *
import json

order_number_blueprint = Blueprint("ordernumber", __name__)

@order_number_blueprint.route("/api/order/<number>")
def api_order_number(number):
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