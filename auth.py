"""Local Mindx account registration and login."""
import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

import streamlit as st

from project_paths import DATA_DIR

DB_PATH = Path(DATA_DIR) / "users.db"
ITERATIONS = 600_000


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def hash_password(password, salt_hex):
    salt = bytes.fromhex(salt_hex)
    result = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ITERATIONS
    )
    return result.hex()


def register_user(username, password):
    username = username.strip()
    if len(username) < 3 or len(username) > 40:
        return False, "Username must be 3?40 characters long."
    if not all(ch.isalnum() or ch in "._-" for ch in username):
        return False, "Use only letters, numbers, dots, underscores or hyphens."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    salt = secrets.token_bytes(16).hex()
    password_hash = hash_password(password, salt)

    try:
        with connect_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt),
            )
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username is already registered."


def verify_user(username, password):
    with connect_db() as conn:
        row = conn.execute(
            "SELECT username, password_hash, salt FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if row is None:
        return None

    stored_username, stored_hash, salt = row
    candidate_hash = hash_password(password, salt)
    if hmac.compare_digest(candidate_hash, stored_hash):
        return stored_username
    return None



def consume_login_ticket(token):
    """Validate and consume a short-lived, single-use HTML login ticket."""
    import datetime
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with connect_db() as conn:
        row = conn.execute(
            "SELECT username, expires_at FROM auth_tickets WHERE token_hash = ?",
            (token_hash,),
        ).fetchone()
        if not row:
            return None
        username, expires_at = row
        conn.execute("DELETE FROM auth_tickets WHERE token_hash = ?", (token_hash,))
    if expires_at <= now:
        return None
    return username

def require_auth():
    """Accept a valid HTML login ticket without showing a Streamlit login screen."""
    user = st.session_state.get("authenticated_user")

    if not user:
        try:
            token = st.query_params.get("ticket")
            if token:
                user = consume_login_ticket(token)
                st.query_params.clear()
                if user:
                    st.session_state["authenticated_user"] = user
        except Exception:
            user = None

    if st.session_state.get("authenticated_user"):
        with st.sidebar:
            st.caption("Signed in as")
            st.write(st.session_state["authenticated_user"])
            if st.button("Log out", key="auth_logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.markdown(
                    '<meta http-equiv="refresh" content="0;url=http://127.0.0.1:5500/logout">',
                    unsafe_allow_html=True,
                )
                st.stop()
        return True

    st.markdown(
        '<meta http-equiv="refresh" content="0;url=http://127.0.0.1:5500/login">',
        unsafe_allow_html=True,
    )
    st.stop()
    return False
