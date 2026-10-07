import os
import time
import random
import smtplib
import hashlib

import streamlit as st
import bcrypt

import sqlite3

from dotenv import load_dotenv

from database import conn, c
from security import hash_password, check_password
from config import (
    LOGIN_LOCK_TIME,
    ACCOUNT_LOCK_TIME,
    OTP_EXPIRY,
    OTP_RESEND_DELAY,
    OTP_WINDOW,
    MAX_OTP_REQUESTS
)

# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("PASSWORD")

# =========================
# SEND OTP EMAIL
# =========================

def send_otp_email(receiver_email, otp):
    try:
        sender_email = os.getenv("EMAIL")
        sender_password = os.getenv("PASSWORD")
        
        subject = "Your OTP Code"
        message = f"Subject: {subject}\n\nYour OTP is: {otp}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        if not sender_email or not sender_password:
            raise Exception("EMAIL or PASSWORD missing in .env")
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,receiver_email,message)
        server.quit()
        return True
    except Exception as e:
        print("OTP EMAIL ERROR:", e)
        return False

# =========================
# GENERATE OTP
# =========================

def generate_otp():

    return str(random.randint(100000, 999999))

# =========================
# HASH OTP
# =========================

def hash_otp(otp):

    return hashlib.sha256(
        otp.encode()
    ).hexdigest()

# =========================
# SAVE OTP
# =========================

def save_otp(email, otp):

    otp_hash = hash_otp(otp)

    expiry = int(time.time()) + OTP_EXPIRY

    c.execute(
        "DELETE FROM otp_codes WHERE email=?",
        (email,)
    )

    c.execute(
        "INSERT INTO otp_codes (email, otp_hash, expiry) VALUES (?, ?, ?)",
        (
            email,
            otp_hash,
            expiry
        )
    )

    conn.commit()

# =========================
# VERIFY OTP
# =========================

def verify_otp(email, otp):

    otp_hash = hash_otp(otp)

    c.execute(
        "SELECT otp_hash, expiry FROM otp_codes WHERE email=?",
        (email,)
    )

    data = c.fetchone()

    if not data:
        return False

    saved_hash, expiry = data

    if int(time.time()) > expiry:
        c.execute(
            "DELETE FROM otp_codes WHERE email=?",
            (email,)
        )

        conn.commit()

        return False

    if otp_hash != saved_hash:
        return False

    c.execute(
        "DELETE FROM otp_codes WHERE email=?",
        (email,)
    )

    conn.commit()

    return True

# =========================
# REGISTER USER
# =========================

def register_user(email, password, first_name, last_name, auth_type="normal"):

    hashed_password = hash_password(password)

    try:

        c.execute(
            """
            INSERT INTO users
            (email, password, first_name, last_name, auth_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                email,
                hashed_password,
                first_name,
                last_name,
                auth_type
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

# =========================
# LOGIN USER
# =========================

def login_user(email, password):

    c.execute(
        """
        SELECT password, first_name, last_name, auth_type
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    user = c.fetchone()

    if not user:
        return None

    hashed_password, first_name, last_name, auth_type = user

    if not check_password(password, hashed_password):
        return None

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "auth_type": auth_type
    }

# =========================
# LOAD LOGIN ATTEMPTS
# =========================

def get_login_attempts(email):

    c.execute(
        """
        SELECT attempts, lock_until
        FROM login_attempts
        WHERE email=?
        """,
        (email,)
    )

    data = c.fetchone()

    if not data:
        return 0, 0

    return data[0], data[1]

# =========================
# SAVE LOGIN ATTEMPTS
# =========================

def save_login_attempts(email, attempts, lock_until=0):

    c.execute(
        """
        INSERT INTO login_attempts
        (email, attempts, lock_until)
        VALUES (?, ?, ?)
        ON CONFLICT(email)
        DO UPDATE SET
            attempts=excluded.attempts,
            lock_until=excluded.lock_until
        """,
        (
            email,
            attempts,
            lock_until
        )
    )

    conn.commit()

# =========================
# RESET LOGIN ATTEMPTS
# =========================

def reset_login_attempts(email):

    c.execute(
        "DELETE FROM login_attempts WHERE email=?",
        (email,)
    )

    conn.commit()

# =========================
# CREATE SESSION TOKEN
# =========================

def create_session_token(email):

    token = hashlib.sha256(
        f"{email}{time.time()}{random.random()}".encode()
    ).hexdigest()

    created_at = int(time.time())

    c.execute(
        "INSERT INTO remembered_sessions (email, session_token, created_at) VALUES (?, ?, ?)",
        (
            email,
            token,
            created_at
        )
    )

    conn.commit()

    return token

# =========================
# HASH SESSION TOKEN
# =========================

def hash_token(token):

    return hashlib.sha256(
        token.encode()
    ).hexdigest()

# =========================
# VERIFY SESSION TOKEN
# =========================

def verify_session_token(token):

    if not token:
        return None

    c.execute(
        """
        SELECT email
        FROM remembered_sessions
        WHERE session_token=?
        """,
        (token,)
    )

    data = c.fetchone()

    if not data:
        return None

    return data[0]

# =========================
# DELETE SESSION TOKEN
# =========================

def delete_session_token(token):

    if not token:
        return

    c.execute(
        "DELETE FROM remembered_sessions WHERE session_token=?",
        (token,)
    )

    conn.commit()

# =========================
# OTP REQUEST LIMIT
# =========================

def can_request_otp(email):

    current_time = int(time.time())

    c.execute(
        """
        SELECT COUNT(*)
        FROM otp_codes
        WHERE email=?
        AND expiry > ?
        """,
        (
            email,
            current_time
        )
    )

    count = c.fetchone()[0]

    if count >= MAX_OTP_REQUESTS:
        return False

    return True

# =========================
# REQUEST OTP
# =========================

def request_otp(email):

    if not can_request_otp(email):
        return False

    otp = generate_otp()

    save_otp(email, otp)

    if send_otp_email(email, otp):
        return True

    return False

# =========================
# OTP RESEND DELAY
# =========================

def can_resend_otp(last_otp_time):

    current_time = int(time.time())

    if current_time - last_otp_time < OTP_RESEND_DELAY:
        return False

    return True