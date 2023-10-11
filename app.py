from flask import Flask, render_template

from api.attractions import attractions_blueprint
from api.attraction_id import attractions_id_blueprint
from api.mrts import mrts_blueprint
from api.user import user_blueprint
from api.auth import auth_blueprint
from api.booking import booking_blueprint
from api.order import order_blueprint
from api.order_number import order_number_blueprint

app = Flask(__name__)
app.register_blueprint(attractions_blueprint)
app.register_blueprint(attractions_id_blueprint)
app.register_blueprint(mrts_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(booking_blueprint)
app.register_blueprint(order_blueprint)
app.register_blueprint(order_number_blueprint)

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

app.run(host="0.0.0.0", port=3000, debug=True)
