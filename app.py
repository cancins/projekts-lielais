from flask import Flask, render_template, request, redirect, session, jsonify
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret123"

db = SQL("sqlite:///datubaze.db")


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
        return redirect("/calendar")

    return "Nepareizi dati"


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    lietotajvards = request.form.get("lietotajvards")
    parole = request.form.get("parole")

    hash_parole = generate_password_hash(parole)

    db.execute(
        "INSERT INTO Login (Lietotajvards, Parole) VALUES (?, ?)",
        lietotajvards, hash_parole
    )

    return redirect("/login")


# ---------------- CALENDAR PAGE ----------------
@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("calendar.html", username=session["username"])


# ---------------- GET EVENTS ----------------
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
        INSERT INTO Kaldendars 
        ("Notikuma datums", "Treninu laiks", Login_id)
        VALUES (?, ?, ?)
    """, date, time, session["user_id"])

    return "OK"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)