import json
from flask import request
import jwt

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

# 取得 Headers 中的 Token
def get_token():
	auth_header = request.headers.get("Authorization")

	print(auth_header)
	if not auth_header or auth_header == "undefined":
		token = None
	else:
		token = auth_header.split()[1]	
	
	return token

def check_auth(token, key="secret"):
	if not token or token == "undefined":
		return None
	else:
		user = jwt.decode(token, key, algorithms=["HS256"])["data"]
		return user