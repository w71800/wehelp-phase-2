from contextlib import contextmanager
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

import mysql.connector as connector
dbconfig = {
	"host": "localhost",
	"user": "root",
	"password": os.environ.get("DB_PASSWORD"),
	"database": "wehelp",
	"pool_name": "pool",
	"pool_size": 5
}
# 建立一個 pool
connection_pool = connector.pooling.MySQLConnectionPool(**dbconfig)

@contextmanager
def connectToDB():
	
	cursor = None
	db = None
	try:
		db = connection_pool.get_connection()
		cursor = db.cursor()

		yield db, cursor
	finally:
		if cursor:
			cursor.close()
		if db:
			db.close()
			
def connectToTP(order):
	prime = order["prime"]
	order = order["order"]
	contact = order["contact"]
	TP_url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
	data = {
		"prime": prime,
		"partner_key": os.environ.get("TP_PARTNER_KEY"),
		"merchant_id": "w71800_CTBC",
		"details":"台北一日遊",
		"amount": order["price"],
		"cardholder": {
				"phone_number": contact["phone"],
				"name": contact["name"],
				"email": contact["email"]
  	}
	}
	headers = {
		"Content-Type": "application/json",
		"x-api-key": "partner_rD3NG5KHlV7RbYLzLbKuEQjLhcrVXxcL0lJCfYRDLtQzvH1FNba3j6gg"
	}
	response = requests.post(TP_url, data = json.dumps(data), headers = headers)
	
	return response