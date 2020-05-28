import os
from flask import Flask, render_template, request
from models import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kmvpbvadlwwnzx:163d32c01378e2740aa1e0a73454c40d863303ba40d1c2607a9354e81dd1577c@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d285f5ll83g7ec"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)   

def main():
    username_input = input("Type your username here:")
    details = User.query.filter_by(username=username_input);
    for detail in details:
        print(f"juicy deets {detail.username}, {detail.password}")
        verification = detail.password
    password_input = input("Type your password here:")
    if password_input == verification:
        print("success")
    else: 
        print("fail")

if __name__ == "__main__":
    with app.app_context():
        main()
