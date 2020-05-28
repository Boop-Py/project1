import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from flask_sqlalchemy import SQLAlchemy

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kmvpbvadlwwnzx:163d32c01378e2740aa1e0a73454c40d863303ba40d1c2607a9354e81dd1577c@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d285f5ll83g7ec"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)   

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


    #    verification = detail.password
    #password_input = input("Type your password here:")
    #if password_input == verification:
     #   print("success")
    #else: 
     #   print("fail")

@app.route("/todolist")
def todolist():
    return render_template("todolist.html")

@app.route("/signup")
def register():
    return render_template("signup.html")
    #db.session.add()

@app.route("/logout")
def logout():
 # session.pop('username', None)
  #flash('You have successful logged out!')
  return redirect("index.html")

@app.route("/test", methods=["POST"])
def testing():
  
    usernameinput = request.form.get("username_input")
    user_count = User.query.filter_by(username=usernameinput).count()

    return render_template("test.html", user_count=user_count)