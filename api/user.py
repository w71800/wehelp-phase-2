from utils.utils import reform_attraction, get_token, check_auth
from models import connectToDB, connector, connectToTP
from flask import Blueprint, request, make_response, jsonify

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/api/user", methods=["POST"])
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