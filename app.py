from flask import Flask, render_template, request, redirect, session, url_for
from datubaze import SQL
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = "parole123"

# Savienojums ar SQLite datubāzi
db = SQL("sqlite:///datubaze.db")

# --- Lietotāju serviss ---
class UserService:
    def __init__(self, db):
        self.db = db

    def autentificet(self, lietotajvards, parole):
        lietotaji = self.db.execute(
            "SELECT * FROM lietotaji WHERE lietotajvards = ? AND parole = ?",
            lietotajvards, parole
        )
        return lietotaji[0] if lietotaji else None

    def lietotajs_eksiste(self, lietotajvards):
        return self.db.execute(
            "SELECT * FROM lietotaji WHERE lietotajvards = ?",
            lietotajvards
        )

    def izveidot_lietotaju(self, lietotajvards, parole):
        return self.db.execute(
            "INSERT INTO lietotaji (lietotajvards, parole) VALUES (?, ?)",
            lietotajvards, parole
        )

userService = UserService(db)

# --- ROUTES ---
@app.route("/")
def index():
    if "user_id" in session:
        # Pēc login aizved uz grafika lapu
        return redirect("/grafiks")
    return redirect("/login")

# --- Login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/grafiks")
        return render_template("login.html")

    # POST
    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")
    hashed_parole = hashlib.md5(parole.encode("utf-8")).hexdigest()

    lietotajs = userService.autentificet(lietotajvards, hashed_parole)

    if lietotajs:
        session["user_id"] = lietotajs["lietotajvards"]
        return redirect("/grafiks")
    else:
        return "Nepareizs lietotājvārds vai parole"

# --- Reģistrācija ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/grafiks")
        return render_template("register.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")
    apst_parole = request.form.get("apst-parole")

    if parole != apst_parole:
        return "Paroles nesakrīt!"

    hashed_parole = hashlib.md5(parole.encode("utf-8")).hexdigest()

    if userService.lietotajs_eksiste(lietotajvards):
        return "Lietotājvārds jau aizņemts!"

    userService.izveidot_lietotaju(lietotajvards, hashed_parole)
    session["user_id"] = lietotajvards
    return redirect("/grafiks")

# --- Grafika lapa ---
@app.route("/grafiks")
def grafiks():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("grafiks.html", username=session["user_id"])

# --- Logout ---
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

# --- Start servera ---
if __name__ == "__main__":
    app.run(debug=True)
