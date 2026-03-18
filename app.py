from flask import Flask, render_template, request, redirect, session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

db = SQL("sqlite:///datubaze.db")

class UserService:
    def __init__(self, db):
        self.db = db

    def autentificet(self, lietotajvards, parole):
        lietotaji = self.db.execute(
            "SELECT * FROM lietotaji WHERE lietotajvards = ?",
            lietotajvards
        )

        if lietotaji and check_password_hash(lietotaji[0]["parole"], parole):
            return lietotaji[0]
        return None

    def lietotajs_eksiste(self, lietotajvards):
        lietotaji = self.db.execute(
            "SELECT * FROM lietotaji WHERE lietotajvards = ?",
            lietotajvards
        )
        return len(lietotaji) > 0

    def izveidot_lietotaju(self, lietotajvards, parole):
        hashed_parole = generate_password_hash(parole)

        return self.db.execute(
            "INSERT INTO lietotaji (lietotajvards, parole) VALUES (?, ?)",
            lietotajvards, hashed_parole
        )

userService = UserService(db)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/grafiks")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/grafiks")
        return render_template("login.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")

    if not lietotajvards or not parole:
        return "Aizpildi visus laukus!"

    lietotajs = userService.autentificet(lietotajvards, parole)

    if lietotajs:
        session["user_id"] = lietotajs["id"]
        session["username"] = lietotajs["lietotajvards"]
        return redirect("/grafiks")
    else:
        return "Nepareizs lietotājvārds vai parole"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/grafiks")
        return render_template("register.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")
    apst_parole = request.form.get("apst-parole")

    if not lietotajvards or not parole or not apst_parole:
        return "Aizpildi visus laukus!"

    if parole != apst_parole:
        return "Paroles nesakrīt!"

    if userService.lietotajs_eksiste(lietotajvards):
        return "Lietotājvārds jau aizņemts!"

    userService.izveidot_lietotaju(lietotajvards, parole)

    return redirect("/login")

@app.route("/grafiks")
def grafiks():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("grafiks.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)