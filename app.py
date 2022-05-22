from flask import Flask


MAX_MONEY = 1000000000

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

with open("secret.txt", "r") as file:
    app.config["SECRET_KEY"] = file.read()
