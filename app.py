from flask import Flask, render_template, request, redirect, session, jsonify
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret123"

db = SQL("sqlite:///datubaze.db")


# ---------------- HOME ----------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/calendar")
    return redirect("/login")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")

    # ✅ HARD LOGIN (requested fix)
    if lietotajvards == "Klievens" and parole == "Ziema2013":
        session["user_id"] = 1
        session["username"] = lietotajvards
        return redirect("/calendar")

    rows = db.execute(
        "SELECT * FROM Login WHERE Lietotajvards = ?",
        lietotajvards
    )

    if len(rows) == 1 and check_password_hash(rows[0]["Parole"], parole):
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["Lietotajvards"]
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


# ---------------- CALENDAR ----------------
@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("calendar.html", username=session["username"])


# ---------------- EVENTS ----------------
@app.route("/events")
def events():
    if "user_id" not in session:
        return jsonify([])

    rows = db.execute("SELECT * FROM Kaldendars")

    events = []
    for r in rows:
        events.append({
            "title": f"🏀 Treniņš ({r['Treninu laiks']})",
            "start": r["Notikuma datums"]
        })

    return jsonify(events)


# ---------------- ADD EVENT ----------------
@app.route("/add_event", methods=["POST"])
def add_event():
    if "user_id" not in session:
        return "Unauthorized", 403

    date = request.form.get("date")
    time = request.form.get("time")

    db.execute("""
        INSERT INTO Kaldendars ("Notikuma datums", "Treninu laiks", Login_id)
        VALUES (?, ?, ?)
    """, date, time, session["user_id"])

    return "OK"


# ---------------- DELETE EVENT ----------------
@app.route("/delete_event", methods=["POST"])
def delete_event():
    if "user_id" not in session:
        return "Unauthorized", 403

    date = request.form.get("date")

    db.execute(
        "DELETE FROM Kaldendars WHERE `Notikuma datums` = ?",
        date
    )

    return "OK"


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)