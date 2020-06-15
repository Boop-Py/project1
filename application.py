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


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)
db.init_app(app)  
hashing = Hashing(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
 




    
    
@app.route("/register", methods = ["GET", "POST"])
def register():
    message = None
    if request.method == "POST":
        newusernameinput = request.form.get("new_username_input")
        newpasswordinput = request.form.get("new_password_input")
        hashed_password = hashing.hash_value(newpasswordinput, salt="dev")
        
        # check user already exists
        check_exists = db.execute("SELECT * FROM users WHERE username = :newusernameinput", 
                                    {"newusernameinput":newusernameinput}).fetchone()   
        if check_exists:
            return render_template("register.html", message = "Already registered.")
            
            # count = user_data.count()
            # if count == 0:
            # new_user = User(username=newusernameinput, password=hashed_password)
            
        # check password is entered   
        elif not newpasswordinput:
            return render_template("register.html", message = "Please enter a password") 
        # user_data = User.query.filter(User.username==newusernameinput)  
        
        # hash the password
        hashed_password = hashing.hash_value(newpasswordinput, salt = "dev")
        
        # insert into database 
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                            {"username":newusernameinput,
                            "password": hashed_password})
                            # db.add(new_user)
        
        # commit changes to database
        db.commit()
        return render_template("register.html", message = "Sucessfully registered. Please log in using the login page.")

    else:
        return render_template("register.html", message = message)

@app.route("/", methods = ["GET", "POST"])
def login():
    message = None    
    if request.method == "POST":
        usernameinput = request.form.get("username_input")
        passwordinput = request.form.get("password_input")
        hashed_password = hashing.hash_value(passwordinput, salt = "dev")
        
        # checks to see if the given username exists.
        check_exists = db.execute("SELECT * FROM users WHERE username = :usernameinput",
                                {"usernameinput":usernameinput})
                                
        exists = check_exists.fetchone()
        print(exists)
        if check_exists:
            print("check password")
            #f hashed_password ==  
            #else:
            #     message = "Please enter valid login details."
        else: 
            message = "Please enter valid login details."  
        # user_data = User.query.filter(User.username==usernameinput, User.password==hashed_password)
           
        #check password is correct

            # remember user

            
            
            # redirect to the search page
        return redirect("/search", code = 302)           
    else:
        return render_template("login.html", message = message)
    return render_template("login.html", message = message)



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
  