import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kmvpbvadlwwnzx:163d32c01378e2740aa1e0a73454c40d863303ba40d1c2607a9354e81dd1577c@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d285f5ll83g7ec" # mysql://username:password@server/db
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()