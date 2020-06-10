import os
import json
from helpers import *
from flask_session import Session
from flask import Flask, session, render_template, request, redirect, url_for
from flask_hashing import Hashing
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from flask_sqlalchemy import SQLAlchemy


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)  


engine = create_engine(os.getenv("DATABASE_URL"))
 

hashing = Hashing(app)


@app.route("/")
def index():
    return render_template("index.html")
    
    
@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    if request.method == "GET":
        if session.get("logged_in"):
            flash("you are already logged in")
            return redirect("/index", code=303)
        else: 
            return render_template("register.html")            
    if request.method == "POST":
        newusernameinput = request.form.get("new_username_input")
        newpasswordinput = request.form.get("new_password_input")
        hashed_password = hashing.hash_value(newpasswordinput, salt="dev")
        user_data = User.query.filter(User.username==newusernameinput)
        count = user_data.count()
        if count == 0:
            new_user = User(username=newusernameinput, password=hashed_password)
            db.add(new_user)
            db.commit()
            message = "Sucessfully registered. Please log in using the login page."
        else:
            message = "Already registered. Please email admin if problem persists."
    return render_template("register.html", message=message)

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
            print("success")
            session["username"]=usernameinput
            return redirect("/search", code=302)
            
        else:
            message = "Please enter valid login details."  
    return render_template("login.html", message=message)

@app.route("/search")
@login_required
def search():
    username=session.get("username")
    #rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
    #                    isbn LIKE :query OR \
    #                    title LIKE :query OR \
    #                    author LIKE :query LIMIT 15",
    #if rows.rowcount == 0:
    #    return render_template("error.html", message="Unable to find any books with that description. ")
    
    #books = rows.fetchall()

    #return render_template("results.html", books=books)
    return render_template("search.html")

@app.route("/todolist")
def todolist():
    return render_template("todolist.html")
    
    





@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

  