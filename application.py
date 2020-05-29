import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from flask_hashing import Hashing
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from flask_sqlalchemy import SQLAlchemy

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
hashing = Hashing(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)   


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
    message = None
    if request.method == "POST":
        usernameinput = request.form.get("username_input")
        passwordinput = request.form.get("password_input")
        hashed_password = hashing.hash_value(passwordinput, salt="dev")
        user_data = User.query.filter(User.username==usernameinput, User.password==hashed_password)
        count = user_data.count()
        print(count)
        if count > 0:
            print("sucess")
            return redirect("/search", code=302)
        else:
            message = "Please enter valid login details."  
    return render_template("login.html", message=message)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/todolist")
def todolist():
    return render_template("todolist.html")

@app.route("/signup")


def register():
    message = None
    #if request.method == "POST":
     #   usernameinput = request.form.get("username_input")
      #  passwordinput = request.form.get("password_input")
       # hashed_password = hashing.hash_value("passwordinput", salt="dev")
        #print (hashed_password)
    #    user_data = User.query.filter(User.username==usernameinput, User.password==passwordinput)
     #   print(user_data)
       # count = user_data.count()
      #  print(count)
        #if count > 0:
         # insert 

 #        new_user = User(
  #                  username = 'newusername',
   #                 password = 'newpassword')
    return render_template("signup.html")


@app.route("/logout")
def logout():
 # session.pop('username', None)
  #flash('You have successful logged out!')
  return redirect("index.html")
