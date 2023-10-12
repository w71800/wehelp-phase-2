from api import *
import jwt
import datetime

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/api/auth", methods=["GET", "PUT"])
def api_auth():
	method = request.method
	key = "secret"
	if(method == "GET"):
		token = get_token()
		
		try:
			user_data = check_auth(token)
			response = { "data": user_data }
		
		except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
			response = { "data": None }
			print(e)
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