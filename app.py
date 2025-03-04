import os
from flask import Flask, render_template

from api.attractions import attractions_blueprint
from api.attraction_id import attractions_id_blueprint
from api.mrts import mrts_blueprint
from api.user import user_blueprint
from api.auth import auth_blueprint
from api.booking import booking_blueprint
from api.order import order_blueprint
from api.order_number import order_number_blueprint
from api.orders import orders_blueprint

blueprints = [
	attractions_blueprint,
	attractions_id_blueprint,
	mrts_blueprint,
	user_blueprint,
	auth_blueprint,
	booking_blueprint,
	order_blueprint,
	order_number_blueprint,
	orders_blueprint
]
app = Flask(__name__)

for blueprint in blueprints:
	app.register_blueprint(blueprint)

app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True


# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")
@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")


port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port, debug=True)
