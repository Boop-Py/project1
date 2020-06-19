import os
import json
import requests
from helpers import *
from flask_session import Session
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_hashing import Hashing
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from flask_sqlalchemy import SQLAlchemy


# check for environment variable
app = Flask(__name__)
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "super secret key"

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
    
        # retrieve values from form
        newusernameinput = request.form.get("new_username_input")
        newpasswordinput = request.form.get("new_password_input")
        
        # hash and salt the password
        hashed_password = hashing.hash_value(newpasswordinput, salt="dev")
        
        # check if user already exists
        check_exists = db.execute("SELECT * FROM users WHERE username = :newusernameinput", 
                                    {"newusernameinput":newusernameinput}).fetchone()   
        if check_exists:
            return render_template("register.html", message = "Unable to register.")
          
        # check password is entered   
        elif not newpasswordinput:
            return render_template("register.html", message = "Please enter a password.") 
        # new_user = User(username=newusernameinput, password=hashed_password)
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
    
        # retrieve values from the form
        username = request.form.get("username_input")
        passwordinput = request.form.get("password_input")
        password = hashing.hash_value(passwordinput, salt = "dev")
        # user_data = User.query.filter(User.username==usernameinput, User.password==hashed_password)  
        
        # check to see if the given username and password exists.
        check_exists = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                                    {"username": username,
                                    "password": password})                            
        exists = check_exists.first()       
        if exists:
            # remember username
            session["user_id"] = exists[0]
            session["user_name"] = exists[1]
      
            # redirect to search page
            return redirect("/search")            
        else:                       
            return render_template("/login.html", message = "Please enter valid login details.")             
    else:
        return render_template("login.html", message = message)
    return render_template("login.html", message = message)

@app.route("/search", methods = ["GET", "POST"])
@login_required
def search():    
    if request.method == "POST":
    
        # retrieve from form
        book = request.form.get("book")      
        
        # format so can we compare part of the query
        like_book_data = "%{}%".format(book)  
        
        # search a case insensitive query.      
        search_query = db.execute("SELECT title, author, isbn, year FROM books WHERE \
                                    title iLIKE :search OR \
                                    author iLIKE :search OR \
                                    isbn iLIKE :search LIMIT 20",
                                    {"search": like_book_data}).fetchall()       
        #search_query = Book_info.query.filter(or_(Book_info.title.ilike(like_book_data), #Book_info.author.ilike(like_book_data), Book_info.isbn.ilike(like_book_data))).limit(20)

        if search_query: 
            return render_template("search.html", message = "Search Results", search = search_query)  
            
        # if there are no matching results, return a message     
        else:
            return render_template("search.html", message = "No books found. Please try again.")                   
    else:
        return render_template("search.html")  
               
@app.route("/book/<isbn>", methods = ["GET", "POST"])    
@login_required
def book(isbn):

    ####BOOK DETAILS####
    # Retrieve the details of the book
    selected_book = db.execute("SELECT isbn, title, author, year, id FROM books WHERE \
                                isbn = :isbn", {"isbn": isbn}).fetchone()
                                
    # collect the book id
    book = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})
    book = book.fetchone()
    
    # returns with a book id with a comma for some reason. remove comma from this.
    book = book[0]
    
    # use the book id to gather reviews
    user_reviews =  db.execute("SELECT users.username, comment, rating \
                                FROM users \
                                INNER JOIN reviews \
                                ON users.id = reviews.user_id \
                                WHERE book_id = :book", 
                                {"book": book})                             
    if user_reviews:
        user_reviews= user_reviews.fetchall()
    else: 
        message = "Be the first to review!"
    ####GOODREADS RATINGS####
    # query the goodreads API with isbn as parameter
    key = os.getenv("GOODREADS_KEY")
    query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})            

    if query.status_code != 200:
        raise Exception("Unable to reach Goodreads API")        
    else: 
        goodreads_data = query.json()
        
    ####USER RATINGS####
    if request.method == "POST":
    
        # retrieve comment and rating from the form
        rating = request.form.get("rating")
        comment = request.form.get("comment")       
        
        # save username 
        user_id = session["user_id"]
       
        # check if user has already reviewed
        check_review_exists = db.execute("SELECT * FROM reviews WHERE user_id = :user_id \
                                        AND book_id = :book_id",
                                        {"user_id": user_id,
                                        "book_id": book}).fetchone()
                         
        if check_review_exists:
            flash("Review already submitted", "warning")
            return render_template("/book/" + isbn)
                       
        # check comment is entered   
        elif not comment:
            return render_template("book.html", message = "Please enter a review") 
         
        # check rating is entered   
        elif not rating:
            return render_template("book.html", message = "Please choose a rating") 
       
        # insert into database
        else: 
            db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                        (:user_id, :book_id, :comment, :rating)",
                        {"user_id": user_id, 
                        "book_id": book, 
                        "comment": comment,                   
                        "rating": rating}) 
            db.commit()
            return redirect("/book/" + isbn)
    return render_template("book.html", selected_book = selected_book, user_reviews = user_reviews, goodreads_data = goodreads_data)
    
@app.route("/api/<isbn>", methods=["GET"])
@login_required
def api_access(isbn):
    # search for api called data and return one row
    api_data = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn}).fetchone()                   
                              
    if api_data:   
    
        # turn it into a python dictionary
        dictlist = dict(api_data.items())
        
        # returns a long decimal for average score that json doesn't like, so get rid of that
        dictlist['average_score'] = float(dictlist['average_score'])
        return jsonify(dictlist)     
    else: 
       return jsonify({"Error 404": "Unable to find ISBN"}), 404
       
@app.route("/todolist")
def todolist():
    return render_template("todolist.html")
    
@app.route("/logout")
@login_required
def logout():    
    session.clear()
    session["user_id"] = False
    return redirect("/", code=302)

