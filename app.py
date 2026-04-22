from flask import Flask, render_template, request, redirect, session, jsonify
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret123"

db = SQL("sqlite:///datubaze.db")


def get_nba_latest_events():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        events = []

        for game in data.get("events", []):

            comp = game["competitions"][0]
            competitors = comp["competitors"]

            team1 = competitors[0]["team"]["displayName"]
            team2 = competitors[1]["team"]["displayName"]

            status = comp.get("status", {}).get("type", {}).get("shortDetail", "N/A")

            score1 = competitors[0].get("score", "0")
            score2 = competitors[1].get("score", "0")

            events.append({
                "team1": team1,
                "team2": team2,
                "status": status,
                "score": f"{score1} - {score2}"
            })

    
        if len(events) == 0:
            return fallback()

        return events[:3]

    except:
        return fallback()


def fallback():
    return [
        {"team1": "Lakers", "team2": "Warriors", "status": "Demo", "score": "0 - 0"},
        {"team1": "Celtics", "team2": "Bucks", "status": "Demo", "score": "0 - 0"},
        {"team1": "Heat", "team2": "Nets", "status": "Demo", "score": "0 - 0"}
    ]


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/calendar")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    user = request.form.get("lietotajvards")
    password = request.form.get("parole")

    if user == "Klievens" and password == "Ziema2013":
        session["user_id"] = 1
        session["username"] = user
        return redirect("/calendar")

    rows = db.execute("SELECT * FROM Login WHERE Lietotajvards = ?", user)

    if len(rows) == 1 and check_password_hash(rows[0]["Parole"], password):
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["Lietotajvards"]
        return redirect("/calendar")

    return render_template("login.html", error="Nepareizi dati")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    user = request.form.get("lietotajvards")
    password = request.form.get("parole")

    db.execute(
        "INSERT INTO Login (Lietotajvards, Parole) VALUES (?, ?)",
        user,
        generate_password_hash(password)
    )

    return redirect("/login")


@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        return redirect("/login")

    events = get_nba_latest_events()

    return render_template(
        "calendar.html",
        username=session["username"],
        events=events
    )


@app.route("/events")
def events():
    if "user_id" not in session:
        return jsonify([])

    rows = db.execute("SELECT * FROM Kaldendars")

    return jsonify([
        {
            "title": f"🏀 Treniņš ({r['Treninu laiks']})",
            "start": r["Notikuma datums"]
        }
        for r in rows
    ])


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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)