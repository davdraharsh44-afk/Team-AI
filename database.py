import sqlite3
import os
import re
import requests

from config import MODEL_NAME

from security import encrypt_text, decrypt_text

# =========================
# MAIN DATABASE
# =========================

conn = sqlite3.connect("users.db", check_same_thread=False)

conn.execute("PRAGMA synchronous=NORMAL;")
conn.execute("PRAGMA temp_store=MEMORY;")

c = conn.cursor()


# =========================
# USERS TABLE
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    auth_type TEXT
)
""")


# =========================
# LOGIN ATTEMPTS TABLE
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS login_attempts (
    email TEXT PRIMARY KEY,
    attempts INTEGER DEFAULT 0,
    lock_until INTEGER DEFAULT 0
)
""")


# =========================
# REMEMBERED SESSIONS
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS remembered_sessions (
    email TEXT,
    session_token TEXT UNIQUE,
    created_at INTEGER
)
""")


# =========================
# OTP CODES
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS otp_codes (
    email TEXT,
    otp_hash TEXT,
    expiry INTEGER
)
""")

conn.commit()

# =========================
# USER DATABASE
# =========================

def get_user_db(email):

    safe_email = email.replace("@", "_").replace(".", "_")

    path = f"data/{safe_email}.db"

    # Fresh connection every time
    conn = sqlite3.connect(path, check_same_thread=False)

    conn.execute("PRAGMA journal_mode=WAL;")

    c = conn.cursor()


    # =========================
    # CHAT HISTORY
    # =========================

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_name TEXT,
        sender TEXT,
        message TEXT
    )
    """)


    # =========================
    # MEMORY
    # =========================

    c.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT
    )
    """)


    # =========================
    # CONVERSATION SUMMARY
    # =========================

    c.execute("""
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary TEXT
    )
    """)


    # =========================
    # PINNED CHATS
    # =========================

    c.execute("""
    CREATE TABLE IF NOT EXISTS pinned_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_name TEXT
    )
    """)

    conn.commit()

    return conn, c

# =========================
# SAVE CHAT
# =========================

def save_chat(email, chat_name, sender, message):

    conn, c = get_user_db(email)

    encrypted_message = encrypt_text(message)

    c.execute(
        "INSERT INTO chat_history (chat_name, sender, message) VALUES (?, ?, ?)",
        (
            chat_name,
            sender,
            encrypted_message
        )
    )

    conn.commit()
    conn.close()

# =========================
# RENAME CHAT
# =========================

def rename_chat_in_db(email, old_name, new_name):

    new_name = re.sub(r'[^A-Za-z0-9 _-]', '', new_name)
    new_name = new_name[:30]

    conn, c = get_user_db(email)

    c.execute(
        "UPDATE chat_history SET chat_name=? WHERE chat_name=?",
        (new_name, old_name)
    )

    conn.commit()
    conn.close()

# =========================
# LOAD CHAT
# =========================

def load_chat(email, chat_name):

    conn, c = get_user_db(email)

    c.execute("""
    SELECT sender, message
    FROM chat_history
    WHERE chat_name=?
    ORDER BY id ASC
    """, (chat_name,))

    data = c.fetchall()

    decrypted_data = []

    for sender, message in data:

        try:
            message = decrypt_text(message)

        except Exception as e:
            print("Decrypt Error:", e)

        decrypted_data.append((sender, message))

    data = decrypted_data

    conn.close()

    return data

# =========================
# REWRITE CHAT
# =========================

def rewrite_chat(email, chat_name, messages):

    conn, c = get_user_db(email)

    c.execute(
        "DELETE FROM chat_history WHERE chat_name=?",
        (chat_name,)
    )

    for sender, message in messages:

        encrypted_message = encrypt_text(message)

        c.execute(
            "INSERT INTO chat_history (chat_name, sender, message) VALUES (?, ?, ?)",
            (
                chat_name,
                sender,
                encrypted_message
            )
        )

    conn.commit()
    conn.close()

# =========================
# SAVE MEMORY
# =========================

def save_memory(email, note):

    conn, c = get_user_db(email)

    encrypted_note = encrypt_text(note)

    c.execute(
        "INSERT INTO memory (note) VALUES (?)",
        (encrypted_note,)
    )

    conn.commit()
    conn.close()

# =========================
# SAVE SUMMARY
# =========================

def save_summary(email, summary):

    conn, c = get_user_db(email)

    c.execute("DELETE FROM summaries")

    c.execute(
        "INSERT INTO summaries (summary) VALUES (?)",
        (summary,)
    )

    conn.commit()
    conn.close()

# =========================
# LOAD SUMMARY
# =========================

def load_summary(email):

    conn, c = get_user_db(email)

    c.execute(
        "SELECT summary FROM summaries ORDER BY id DESC LIMIT 1"
    )

    data = c.fetchone()

    conn.close()

    if data:
        return data[0]

    return ""

# =========================
# LOAD MEMORY
# =========================

def load_memory(email):

    conn, c = get_user_db(email)

    c.execute("SELECT note FROM memory")

    data = []

    for row in c.fetchall():

        try:
            data.append(decrypt_text(row[0]))

        except:
            pass

    conn.close()

    return data

# =========================
# SAVE PINNED CHAT
# =========================

def save_pinned_chat(email, chat_name):

    conn, c = get_user_db(email)

    c.execute(
        "SELECT * FROM pinned_chats WHERE chat_name=?",
        (chat_name,)
    )

    existing = c.fetchone()

    if not existing:

        c.execute(
            "INSERT INTO pinned_chats (chat_name) VALUES (?)",
            (chat_name,)
        )

    conn.commit()
    conn.close()

# =========================
# REMOVE PINNED CHAT
# =========================

def remove_pinned_chat(email, chat_name):

    conn, c = get_user_db(email)

    c.execute(
        "DELETE FROM pinned_chats WHERE chat_name=?",
        (chat_name,)
    )

    conn.commit()
    conn.close()

# =========================
# LOAD PINNED CHATS
# =========================

def load_pinned_chats(email):

    conn, c = get_user_db(email)

    c.execute("SELECT chat_name FROM pinned_chats")

    data = [row[0] for row in c.fetchall()]

    conn.close()

    return data

# =========================
# SMART SAVE MEMORY
# =========================

def smart_save_memory(email, message):

    existing = load_memory(email)

    for mem in existing:

        if message.lower().strip() == mem.lower().strip():
            return False

    if len(existing) >= 200:
        return False

    save_memory(email, message)

    return True

# =========================
# GET ALL CHAT NAMES
# =========================

def get_all_chat_names(email):

    conn, c = get_user_db(email)

    c.execute("SELECT DISTINCT chat_name FROM chat_history")

    chats = [row[0] for row in c.fetchall()]

    conn.close()

    return chats

# =========================
# EXTRACT MEMORY WITH AI
# =========================

def extract_memory_with_ai(user_message):

    try:

        prompt = f"""
Extract important long-term memory from this message.

Message:
{user_message}

Rules:
- Only keep useful personal information
- Ignore temporary chat
- Keep memories short
- One memory per line

Examples:
User likes cricket
User name is Harsh
User studies engineering

Memories:
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            },
            timeout=60
        )

        data = response.json()

        memory_text = data.get("response", "").strip()

        if not memory_text:
            return []

        memories = [
            m.strip()
            for m in memory_text.split("\n")
            if m.strip()
        ]

        return memories

    except Exception as e:

        print("Memory Extract Error:", e)

        return []