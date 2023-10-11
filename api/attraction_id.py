from utils.utils import reform_attraction, get_token, check_auth
from models import connectToDB, connector, connectToTP
from flask import Blueprint, request, make_response, jsonify

attractions_id_blueprint = Blueprint("attraction_id", __name__)

@attractions_id_blueprint.route("/api/attraction/<attractionId>")
def api_attraction＿id(attractionId):
	with connectToDB() as (db, cursor):
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
				return make_response(jsonify(response), 400)
			
			else:
				response = {
					"data": reform_attraction(result[0])
				}
				return make_response(jsonify(response), 200)
			
		except Exception as e:
			response = { 
				"error": True, 
				"message": f"伺服器發生內部錯誤：{e}"
			}
			return make_response(jsonify(response), 500)