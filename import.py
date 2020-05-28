import csv
import time

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kmvpbvadlwwnzx:163d32c01378e2740aa1e0a73454c40d863303ba40d1c2607a9354e81dd1577c@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d285f5ll83g7ec" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(f)

    for isbn, title, author, year in reader:
        book = book_info(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"{title} by {author} created in {year}. ISBN: {isbn}")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()