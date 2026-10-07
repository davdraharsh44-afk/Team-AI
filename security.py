import os
import bcrypt

from cryptography.fernet import Fernet
from dotenv import load_dotenv

# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise Exception("FERNET_KEY missing in .env")


# =========================
# ENCRYPTION
# =========================

cipher = Fernet(FERNET_KEY.encode())

# =========================
# ENCRYPT TEXT
# =========================

def encrypt_text(text):

    return cipher.encrypt(text.encode()).decode()

# =========================
# DECRYPT TEXT
# =========================

def decrypt_text(text):

    return cipher.decrypt(text.encode()).decode()

# =========================
# PASSWORD HASH
# =========================

def hash_password(password):

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

# =========================
# PASSWORD CHECK
# =========================

def check_password(password, hashed_password):

    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )