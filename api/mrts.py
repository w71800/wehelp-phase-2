from api import *

mrts_blueprint = Blueprint("mrts", __name__)

@mrts_blueprint.route("/api/mrts")
def api_mrts():
	response = None
	with connectToDB() as (db, cursor):
		try:
			sql = "SELECT mrt, count(name) from resorts GROUP BY mrt ORDER BY count(name) DESC"
			cursor.execute(sql)
			result = cursor.fetchall()

			result_container = [ item[0] for item in result ]
			result_container = list(filter(lambda x : x != "empty", result_container))
			response = {
				"data": result_container
			}
			return make_response(jsonify(response), 200)
		
		except connector.Error as e:
			response = {
					"error": True, 
					"message": f"伺服器發生內部錯誤：{e}"
					}
			return make_response(jsonify(response), 500)