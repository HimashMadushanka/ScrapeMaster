from flask import Flask, render_template, request, redirect, session
import mysql.connector
import requests
from bs4 import BeautifulSoup
import csv
from flask import Response

app = Flask(__name__)
app.secret_key = "secretkey"

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # IMPORTANT: leave empty
    database="scraper_app"
)
cursor = db.cursor(dictionary=True)

# ==========================
# Home -> Login
# ==========================
@app.route("/")
def home():
    return render_template("login.html")


# ==========================
# Register
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, password))
        db.commit()

        return redirect("/")

    return render_template("register.html")


# ==========================
# Login
# ==========================
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    sql = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()

    if user:
        session["user"] = user["username"]
        return redirect("/dashboard")
    else:
        return "Invalid Credentials"


# ==========================
# Dashboard
# ==========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template("dashboard.html", books=books, user=session["user"])


# ==========================
# Run Scraper
# ==========================
@app.route("/scrape", methods=["POST"])
def scrape():
    if "user" not in session:
        return redirect("/")

    limit = int(request.form["limit"])

    response = requests.get("http://books.toscrape.com/catalogue/page-1.html")
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    count = 0

    for book in books:
        if count >= limit:
            break

        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").text
        availability = book.find("p", class_="instock availability").text.strip()
        rating = book.find("p")["class"][1]

        sql = """
        INSERT INTO books (title, price, rating, availability)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (title, price, rating, availability))
        count += 1

    db.commit()

    return redirect("/dashboard")


@app.route("/download")
def download():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    def generate():
        data = csv.writer(open("books.csv", "w", newline=""))
        yield "Title,Price,Rating,Availability\n"
        for book in books:
            row = f"{book['title']},{book['price']},{book['rating']},{book['availability']}\n"
            yield row

    return Response(generate(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=books.csv"})
# ==========================
# Logout
# ==========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)