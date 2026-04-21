from flask import Flask, render_template, request, redirect, session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret123"

db = SQL("sqlite:///datubaze.db")


# ---------------- SĀKUMS ----------------
@app.route("/")
def index():
    return redirect("/login")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")

    rows = db.execute(
        "SELECT * FROM Login WHERE Lietotajvards = ?",
        lietotajvards
    )

    if len(rows) == 1 and check_password_hash(rows[0]["Parole"], parole):
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["Lietotajvards"]

        # 👉 ŠIS IR GALVENAIS
        return redirect("/calendar")

    return "Nepareizs login"


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")

    db.execute(
        "INSERT INTO Login (Lietotajvards, Parole) VALUES (?, ?)",
        lietotajvards,
        generate_password_hash(parole)
    )

    return redirect("/login")


# ---------------- KALENDĀRS ----------------
@app.route("/calendar")
def calendar():

    # 👉 JA NAV IELOGOJIES → atpakaļ uz login
    if "user_id" not in session:
        return redirect("/login")

    return render_template("calendar.html", username=session["username"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)