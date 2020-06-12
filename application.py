import os
import json
from helpers import *
from flask_session import Session
from flask import Flask, session, render_template, request, redirect, url_for
from flask_hashing import Hashing
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from flask_sqlalchemy import SQLAlchemy


# check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)  


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

 
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

    # salts and hashes the new password
    if request.method == "POST":
        newusernameinput = request.form.get("new_username_input")
        newpasswordinput = request.form.get("new_password_input")
        hashed_password = hashing.hash_value(newpasswordinput, salt="dev")
        user_data = User.query.filter(User.username==newusernameinput)
        
        # checks if user already exists
        count = user_data.count()
        if count == 0:
            new_user = User(username=newusernameinput, password=hashed_password)
            
            # commit changes to database
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
        
        # checks to see if the given username/password combination exists.
        user_data = User.query.filter(User.username==usernameinput, User.password==hashed_password)
        count = user_data.count()
        if count > 0:
            session["username"]=usernameinput
            return redirect("/search", code=302)           
        else:
            message = "Please enter valid login details."  
    return render_template("login.html", message=message)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():    
    if request.method == "POST":
        book = request.form.get("book")       
        # format so can we compare part of the query
        like_book_data = "%{}%".format(book)        
        # search a case insensitive query. equiv to SELECT title, author, isbn, year FROM books WHERE title LIKE '%eg%' OR author LIKE '%search%' OR isbn LIKE '%search%' LIMIT 20;
        search_query = Book_info.query.filter(or_(Book_info.title.ilike(like_book_data), Book_info.author.ilike(like_book_data), Book_info.isbn.ilike(like_book_data))).limit(20)
        search = search_query.all()

        # if there are no matching results, return a message 
        if search_query.count() == 0:
      
            return render_template("search.html", message="No books found. Please try again.")
     
        else: 
            return render_template("search.html", message="Search Results", search=search)  
            
    else:
        return render_template("search.html")  

@app.route("/todolist")
def todolist():
    return render_template("todolist.html")
    
@app.route("/logout")
def logout():    
    session.clear()
    return render_template("login.html", message="Signed out sucessfully!")

#@app.route("/test", methods=["GET", "POST"])
#def test():
#return render_template(.....html)

@app.route("/book/<isbn>", methods=["GET", "POST"])    
@login_required
def book():
    if request.method == "POST":
    
        return render_template(index.html)
  