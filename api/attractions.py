from utils.utils import reform_attraction, get_token, check_auth
from models import connectToDB, connector, connectToTP
from flask import Blueprint, request, make_response, jsonify

attractions_blueprint = Blueprint("attractions", __name__)

@attractions_blueprint.route("/api/attractions/")
def api_attractions():
	with connectToDB() as (db, cursor):
		page = int(request.args.get("page")) if request.args.get("page") else None
		keyword = request.args.get("keyword")

		if page == None:
			response = {
				"error": True, 
				"message": "未輸入頁數"
			}

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

			return make_response(jsonify(response), 200)
			
		except connector.Error as e:
			response = {
				"error": True, 
				"message": f"伺服器發生內部錯誤：{e}"
				}
			return make_response(jsonify(response), 500)