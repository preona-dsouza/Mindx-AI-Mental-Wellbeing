import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, request, redirect, url_for, render_template, session
from auth import register_user, verify_user, DB_PATH

import subprocess
import sys
import socket
import time
from pathlib import Path


app = Flask(__name__)
secret_file = DB_PATH.parent / "flask_session_secret.txt"
secret_file.parent.mkdir(parents=True, exist_ok=True)
if secret_file.exists():
    app.secret_key = secret_file.read_text(encoding="utf-8").strip()
else:
    secret = secrets.token_hex(32)
    secret_file.write_text(secret, encoding="utf-8")
    app.secret_key = secret

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def setup_tickets():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auth_tickets (
                token_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)

def make_ticket(username):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    expiry = (now + timedelta(minutes=2)).isoformat()
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute(
            "DELETE FROM auth_tickets WHERE expires_at < ?",
            (now.isoformat(),)
        )
        conn.execute(
            "INSERT INTO auth_tickets(token_hash, username, expires_at) "
            "VALUES (?, ?, ?)", (token_hash, username, expiry)
        )
    return token

@app.route("/")
def index():
    return render_template("home.html", message=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    setup_tickets()
    if request.method == "GET":
        message = ("Account created. You can now log in."
                   if request.args.get("registered") else None)
        return render_template("home.html", message=message)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = verify_user(username, password)
    if not user:
        return render_template(
            "home.html", message="Incorrect username or password."
        ), 401

    session.clear()
    session["username"] = user
    return redirect(url_for("choose"))

@app.route("/register", methods=["GET", "POST"])
def register():
    setup_tickets()
    if request.method == "GET":
        return render_template("register.html", message=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    if password != confirm:
        return render_template(
            "register.html", message="Passwords do not match."
        ), 400

    ok, message = register_user(username, password)
    if not ok:
        return render_template("register.html", message=message), 400

    return redirect(url_for("login", registered="1"))

@app.route("/choose")
def choose():
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("login.html", message=None)




BASE_DIR = Path(__file__).resolve().parent

def ensure_streamlit_running(mode):
    apps = {
        "text": ("chatbot.py", 8501),
        "voice": ("app.py", 8502),
    }

    script, port = apps[mode]

    # Reuse the app if something is already listening.
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            return port

    subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            str(BASE_DIR / script),
            "--server.port", str(port),
            "--server.address", "127.0.0.1",
            "--server.headless", "true",
        ],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=(
            subprocess.CREATE_NO_WINDOW
            if sys.platform == "win32" else 0
        ),
    )

    for _ in range(30):
        time.sleep(1)
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return port

    raise RuntimeError(f"Streamlit app did not start on port {port}")


@app.route("/launch/<mode>")
def launch(mode):
    if mode not in ("text", "voice"):
        return "Unknown interface", 404

    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    try:
        port = ensure_streamlit_running(mode)
    except RuntimeError as exc:
        app.logger.exception("Could not start Streamlit")
        return str(exc), 500

    setup_tickets()
    token = make_ticket(username)

    return redirect(
        f"http://127.0.0.1:{port}/?ticket={token}"
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    setup_tickets()
    app.run(host="127.0.0.1", port=5500, debug=False)
