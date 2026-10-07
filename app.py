import streamlit as st
import html
import requests
import threading
import re
import random
from dotenv import load_dotenv
import os
from streamlit_oauth import OAuth2Component
from PIL import Image
import bcrypt
import time
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
# =========================
# PROJECT MODULES
# =========================
from config import *
from database import *
from security import *
from auth import *
from gemini import *
from ollama_ai import *
from image_ai import *
from pdf import *
from internet import *
from voice import *
from export import *
from ui import *



load_dotenv()


# ✅ Create data folder if not exists
if not os.path.exists("data"):
    os.makedirs("data")
st.set_page_config(page_title="Harsh AI Ultra Pro",page_icon="🤖",layout="wide",initial_sidebar_state="auto")
# ================= SESSION =================
if "ai_generating" not in st.session_state:
    st.session_state.ai_generating = False
if "login" not in st.session_state:
    st.session_state.login = False
if "register" not in st.session_state:
    st.session_state.register = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "theme" not in st.session_state:
    st.session_state.theme = "Pink"
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "first_name" not in st.session_state:
    st.session_state.first_name = ""
if "profile_pic" not in st.session_state:
    st.session_state.profile_pic = ""
if "input" not in st.session_state:
    st.session_state.input = ""
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "memory" not in st.session_state:
    st.session_state.memory = []
if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = ""
if "personality" not in st.session_state:
    st.session_state.personality = "Normal"
if "remember_me" not in st.session_state:
    st.session_state.remember_me = False
if "forgot" not in st.session_state:
    st.session_state.forgot = False
if "otp" not in st.session_state:
    st.session_state.otp = ""
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "lock_until" not in st.session_state:
    st.session_state.lock_until = 0
if "otp_time" not in st.session_state:
    st.session_state.otp_time = 0
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False
if "last_msg_time" not in st.session_state:
    st.session_state.last_msg_time = 0
if "spam_count" not in st.session_state:
    st.session_state.spam_count = 0
if "spam_block_until" not in st.session_state:
    st.session_state.spam_block_until = 0
if "ai_request_count" not in st.session_state:
    st.session_state.ai_request_count = 0
if "ai_request_window" not in st.session_state:
    st.session_state.ai_request_window = 0
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()
if "session_token" not in st.session_state:
    st.session_state.session_token = os.urandom(24).hex()
if "google_login_started" not in st.session_state:
    st.session_state.google_login_started = False
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "last_uploaded_type" not in st.session_state:
    st.session_state.last_uploaded_type = None
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = ""
if "internet_on" not in st.session_state:
    st.session_state.internet_on = True
if "pinned_chats" not in st.session_state:
    st.session_state.pinned_chats = []
if "otp_attempts" not in st.session_state:
    st.session_state.otp_attempts = 0
if "otp_send_count" not in st.session_state:
    st.session_state.otp_send_count = 0
if "otp_send_window" not in st.session_state:
    st.session_state.otp_send_window = 0
if "last_otp_sent_time" not in st.session_state:
    st.session_state.last_otp_sent_time = 0

apply_theme()
# ================= SECURE AUTO LOGIN =================
if not st.session_state.login:
    current_token = hash_token(st.session_state.session_token)
    c.execute(
        """
        SELECT email
        FROM remembered_sessions
        WHERE session_token=?
        AND created_at > ?
        """,(current_token,int(time.time()) - (30 * 24 * 60 * 60)))
    remembered_user = c.fetchone()
    if remembered_user:
        saved_email = remembered_user[0]
        c.execute("SELECT * FROM users WHERE email=?",(saved_email,))
        user = c.fetchone()
        if user:
            st.session_state.first_name = user[2]
            st.session_state.login = True
            st.session_state.email = saved_email
            all_chats = get_all_chat_names(saved_email)
            if not all_chats:
                st.session_state.chats = {"Chat 1": []}
            else:
                st.session_state.chats = {}
                for chat in all_chats:
                    st.session_state.chats[chat] = load_chat(saved_email, chat)
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            st.session_state.memory = load_memory(saved_email)
            st.session_state.conversation_summary = load_summary(saved_email)
            st.session_state.pinned_chats = load_pinned_chats(saved_email)
# ================= LOGIN =================
if not st.session_state.login and not st.session_state.register and not st.session_state.forgot:
    st.markdown('<p class="main-title">🤖 Harsh AI Ultra Pro</p>', unsafe_allow_html=True)
    email = st.text_input("Enter Gmail")
    show_password = st.checkbox("👁 Show Password")
    remember = st.checkbox("Remember Me")
    if show_password:
        password = st.text_input("Enter Password")
    else:
        password = st.text_input("Enter Password", type="password")
    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    # ================= NORMAL LOGIN =================
    if st.button("Login / Register"):
        if time.time() < st.session_state.lock_until:
            remaining = int(st.session_state.lock_until - time.time())
            st.error(f"🚫 Too many attempts. Try again after {remaining} seconds.")
            st.stop()
        if st.session_state.login_attempts >= 5:
            st.error("🚫 Too many attempts. Please wait.")
            st.stop()
        email = email.strip().lower()
        if not email or not password:
            st.error("❌ Please enter email and password")
        elif not is_valid_email(email):
            st.error("❌ Enter valid email")
        elif (len(password) < 10 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password)  or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*]", password)):
            st.error("❌ Password must contain uppercase letter and number")
        else:
            c.execute("SELECT attempts, lock_until FROM login_attempts WHERE email=?",(email,))
            lock_row = c.fetchone()
            if lock_row:
                attempts, lock_until = lock_row
                if lock_until > int(time.time()):
                    remaining = int((lock_until - int(time.time())) / 60) + 1
                    st.error(f"🚫 Account locked. Try again in {remaining} minutes.")
                    st.stop()
            c.execute("SELECT * FROM users WHERE email=?",(email,))
            user = c.fetchone()
            if not user:
                st.warning("⚠️ Email not registered. Please register first.")
                st.session_state.email = email
                st.session_state.password = password
                st.session_state.register = True
            else:
                stored_password = user[1]
                auth_type = user[4] if len(user) > 4 else "normal"
                if auth_type == "google":
                    st.error("❌ Please login using Google button")
                elif bcrypt.checkpw(password.encode(),stored_password.encode()):
                    st.session_state.login_attempts = 0
                    st.session_state.first_name = user[2]
                    c.execute("DELETE FROM login_attempts WHERE email=?",(email,))
                    conn.commit()
                    st.session_state.login = True
                    st.session_state.session_token = os.urandom(24).hex()
                    st.session_state.email = email
                    st.session_state.internet_on = True
                    all_chats = get_all_chat_names(email)
                    if not all_chats:
                        st.session_state.chats = {"Chat 1": []}
                    else:
                        st.session_state.chats = {}
                        for chat in all_chats:
                            st.session_state.chats[chat] = load_chat(email, chat)
                    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                    st.session_state.memory = load_memory(email)
                    st.session_state.conversation_summary = load_summary(email)
                    st.session_state.pinned_chats = load_pinned_chats(email)
                    if remember:
                        c.execute("DELETE FROM remembered_sessions WHERE email=?",(email,))
                        hashed_token = hash_token(st.session_state.session_token)
                        c.execute("INSERT INTO remembered_sessions VALUES (?, ?, ?)",(email,hashed_token,int(time.time())))
                        conn.commit()
                    st.success("✅ Login Successful")
                    st.rerun()
                else:
                    c.execute("SELECT attempts FROM login_attempts WHERE email=?",(email,))
                    row = c.fetchone()
                    if row:
                        attempts = row[0] + 1
                    else:
                        attempts = 1
                    if attempts >= 5:
                        c.execute(
                            """
                            INSERT OR REPLACE INTO login_attempts
                            VALUES (?, ?, ?)
                            """,(email,attempts,int(time.time()) + ACCOUNT_LOCK_TIME))
                        conn.commit()
                        st.error("🚫 Too many failed attempts. Account locked for 15 minutes.")
                    else:
                        c.execute(
                            """
                            INSERT OR REPLACE INTO login_attempts
                            VALUES (?, ?, ?)
                            """,(email,attempts,0))
                        conn.commit()
                    st.session_state.login_attempts += 1
                    if st.session_state.login_attempts >= 5:
                        st.session_state.lock_until = time.time() + LOGIN_LOCK_TIME
                        st.error("🚫 Account locked for 5 minutes.")
                    else:
                        st.error(f"❌ Wrong Password ({st.session_state.login_attempts}/5)")
    # ================= GOOGLE LOGIN =================
    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    oauth2 = OAuth2Component(
        CLIENT_ID,
        CLIENT_SECRET,
        "https://accounts.google.com/o/oauth2/auth",
        "https://oauth2.googleapis.com/token",
    )
    try:
        result = oauth2.authorize_button(name="🔵 Login with Google",icon="https://www.google.com/favicon.ico",redirect_uri=REDIRECT_URI,scope="openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",key="google_login",extras_params={"prompt": "select_account"},)
    except Exception as e:
        if "STATE" in str(e):
            st.warning("⚠️ Google session expired. Please click login again.")
            st.stop()
        else:
            st.error(f"Google Login Error: {str(e)}")
            st.stop()
    if result:
        st.session_state.google_login_started = True
    if result and "token" in result:
        token = result["token"]
        id_token_jwt = token.get("id_token")
        if id_token_jwt:
            try:
                # 🔒 VERIFY TOKEN WITH GOOGLE
                idinfo = id_token.verify_oauth2_token(id_token_jwt,google_requests.Request(),CLIENT_ID,clock_skew_in_seconds=10)
                if not idinfo.get("email_verified"):
                    st.error("❌ Google email not verified")
                    st.stop()
                # ✅ VERIFIED USER INFO
                email = idinfo.get("email")
                name = idinfo.get("name", "User")
                picture = idinfo.get("picture", "")
                if picture and not picture.startswith("https://"):
                    picture = ""
                if not picture:
                    picture = "https://via.placeholder.com/80"
            except Exception as e:
                st.error(f"❌ Google Verify Error: {str(e)}")
                st.stop()
            st.session_state.login = True
            st.session_state.session_token = os.urandom(24).hex()
            st.session_state.email = email
            st.session_state.first_name = name
            st.session_state.profile_pic = picture
            st.session_state.internet_on = True
            # ✅ LOAD CHATS AFTER GOOGLE LOGIN
            all_chats = get_all_chat_names(email)
            if not all_chats:
                st.session_state.chats = {"Chat 1": []}
            else:
                st.session_state.chats = {}
                for chat in all_chats:
                    st.session_state.chats[chat] = load_chat(email, chat)
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            st.session_state.memory = load_memory(email)
            st.session_state.conversation_summary = load_summary(email)
            st.session_state.pinned_chats = load_pinned_chats(email)
            # DB check
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()
            if not user:
                c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (email,"",name,"","google"))
                conn.commit()
            st.success(f"✅ Logged in as {email}")
            st.rerun()
        else:
            st.error("❌ ID Token not found")
    elif result:
        st.error("❌ Access token not found")
    # ================= FORGOT PASSWORD =================
    if st.button("Forgot Password?"):
        st.session_state.forgot = True
elif st.session_state.register:
    st.markdown('<p class="main-title">Enter Your Name</p>', unsafe_allow_html=True)
    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    if st.button("Submit"):
        if not first.strip() or not last.strip():
            st.error("❌ Enter valid name")
            st.stop()
        email = st.session_state.email.strip().lower()
        # 🔍 Check email already exists
        c.execute("SELECT * FROM users WHERE email=?", (st.session_state.email,))
        existing_user = c.fetchone()
        if existing_user:
            st.error("❌ Email already exists")
        else:
            # 🔐 Hash password
            hashed_password = bcrypt.hashpw(st.session_state.password.encode(),bcrypt.gensalt(rounds=12)).decode()
            # 💾 Save to database
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (st.session_state.email,hashed_password,first,last,"normal"))
            conn.commit()
            # ✅ Auto login
            st.session_state.first_name = first
            st.session_state.login = True
            st.session_state.session_token = os.urandom(24).hex()
            st.session_state.register = False
            st.success("✅ Registration Successful")
            st.rerun()
elif st.session_state.forgot:
    st.markdown('<p class="main-title">Reset Password</p>', unsafe_allow_html=True)
    reset_email = st.text_input("Enter your email")
    new_password = st.text_input("Enter new password", type="password")
    entered_otp = st.text_input("Enter OTP")
    if st.button("Send OTP"):
        current_time = time.time()
        if current_time - st.session_state.otp_send_window > OTP_WINDOW:
            st.session_state.otp_send_count = 0
            st.session_state.otp_send_window = current_time
        if st.session_state.otp_send_count >= MAX_OTP_REQUESTS:
            st.error("🚫 Maximum 3 OTP requests allowed in 10 minutes.")
            st.stop()
        if not reset_email:
            st.error("❌ Enter email first")
        else:
            # ✅ check email exists
            c.execute("SELECT * FROM users WHERE email=?", (reset_email,))
            user = c.fetchone()
            if not user:
                st.error("❌ Email not registered")
            else:
                otp = str(random.randint(100000, 999999))
                st.session_state.otp_send_count += 1
                otp_hash = hash_otp(otp)
                c.execute("DELETE FROM otp_codes WHERE email=?",(reset_email,))
                c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)",(reset_email,otp_hash,int(time.time()) + OTP_EXPIRY))
                conn.commit()
                st.session_state.otp_time = time.time()
                st.session_state.otp_sent = True
                email_sent = send_otp_email(reset_email, otp)
                st.session_state.last_otp_sent_time = time.time()
                if email_sent:
                    st.success(f"✅ OTP sent to {reset_email}")
                else:
                    st.error("❌ Failed to send OTP email")
    if st.session_state.otp_sent:
        if st.button("Resend OTP"):
            current_time = time.time()
            if current_time - st.session_state.last_otp_sent_time < OTP_RESEND_DELAY:
                remaining = int(OTP_RESEND_DELAY - (current_time - st.session_state.last_otp_sent_time))
                st.error(f"⏳ Please wait {remaining} seconds before requesting another OTP.")
                st.stop()
            otp = str(random.randint(100000, 999999))
            otp_hash = hash_otp(otp)
            c.execute("DELETE FROM otp_codes WHERE email=?",(reset_email,))
            c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)",(reset_email,otp_hash,int(time.time()) + 300))
            conn.commit()
            st.session_state.otp_time = time.time()
            email_sent = send_otp_email(reset_email,otp)
            st.session_state.last_otp_sent_time = current_time
            if email_sent:
                st.success("🔁 New OTP sent!")
            else:
                st.error("❌ Failed to resend OTP")
    if st.button("Reset Password"):
        c.execute("SELECT otp_hash, expiry FROM otp_codes WHERE email=?",(reset_email,))
        otp_row = c.fetchone()
        if not reset_email or not new_password or not entered_otp:
            st.error("❌ Fill all fields")

        elif (not otp_row or otp_row[1] < int(time.time()) or otp_row[0] != hash_otp(entered_otp)):
            st.session_state.otp_attempts += 1
            if st.session_state.otp_attempts >= 5:
                st.error("🚫 Too many OTP attempts.")
                st.stop()
            st.error(f"❌ Invalid OTP ({st.session_state.otp_attempts}/5)")
        elif (len(new_password) < 10 or not re.search(r"[A-Z]", new_password) or not re.search(r"[a-z]", new_password) or not re.search(r"[0-9]", new_password) or not re.search(r"[!@#$%^&*]", new_password)):
            st.error("❌ Password must contain uppercase, lowercase, number and symbol")
        else:
            c.execute("SELECT * FROM users WHERE email=?", (reset_email,))
            user = c.fetchone()
            if user:
                hashed_password = bcrypt.hashpw(new_password.encode(),bcrypt.gensalt(rounds=12)).decode()
                c.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, reset_email))
                conn.commit()
                st.success("✅ Password updated successfully")
                st.session_state.otp_attempts = 0
                st.session_state.otp_sent = False
                st.session_state.otp_time = 0
                # reset states
                st.session_state.forgot = False
                c.execute("DELETE FROM otp_codes WHERE email=?",(reset_email,))
                conn.commit()
            else:
                st.error("❌ Email not found")
# ================= MAIN APP =================
# 🔒 Auto session timeout (30 min)
if (st.session_state.login and time.time() - st.session_state.last_activity > SESSION_TIMEOUT):
    st.session_state.clear()
    st.session_state.login = False
    st.warning("⏳ Session expired. Please login again.")
    st.rerun()

if st.session_state.login:
    with st.sidebar:
    # 🔥 MULTI CHAT UI START
        st.markdown("## 💬 Chats")
        st.markdown("""
        <style>
        div[data-testid="stTextInput"] input{
            height:35px;
            font-size:14px;
        }
        </style>
        """, unsafe_allow_html=True)
        search = st.text_input(
            "Search chats",
            placeholder="🔍 Search chats...",
            key="chat_search",
            label_visibility="collapsed"
        )
        # ➕ New Chat
        if st.button("➕ New Chat"):
            i = 1
            while f"Chat {i}" in st.session_state.chats:
                i += 1
            new_name = f"Chat {i}"
            st.session_state.chats[new_name] = []
            st.session_state.current_chat = new_name
            # OPTIONAL: remove if you don't want default message
            # save_chat(st.session_state.email, new_name, "system", "Chat created")
        # 📂 Chat List
        sorted_chats = (st.session_state.pinned_chats + [c for c in st.session_state.chats.keys() if c not in st.session_state.pinned_chats])
        for chat_name in sorted_chats.copy():
            # 🔍 Search filter
            if search.lower() not in chat_name.lower():
                continue
            col1, col2, col3 = st.columns([4,1,1])
            with col1:
                if st.button(chat_name, key=chat_name):
                    st.session_state.current_chat = chat_name
                    loaded_chat = load_chat(st.session_state.email, chat_name)
                    st.session_state.chats[chat_name] = loaded_chat if loaded_chat else []
                    st.rerun()
                # ✏️ Rename button
                if st.button("✏️", key=f"rename_btn_{chat_name}"):
                    st.session_state.rename_target = chat_name
            with col2:
                pin_icon = "📌" if chat_name not in st.session_state.pinned_chats else "❌"
                if st.button(pin_icon, key=f"pin_{chat_name}"):
                    # UNPIN
                    if chat_name in st.session_state.pinned_chats:
                        st.session_state.pinned_chats.remove(chat_name)
                        remove_pinned_chat(st.session_state.email,chat_name)
                    # PIN
                    else:
                        st.session_state.pinned_chats.append(chat_name)
                        save_pinned_chat(st.session_state.email,chat_name)
                    st.rerun()
            with col3:
                if st.button("❌", key=f"del_{chat_name}"):
                    if len(st.session_state.chats) > 1:
                        # 🔥 delete from DB
                        conn_user, c_user = get_user_db(st.session_state.email)
                        c_user.execute("DELETE FROM chat_history WHERE chat_name=?",(chat_name,))
                        conn_user.commit()
                        conn_user.close()
                        # remove from pinned if pinned
                        if chat_name in st.session_state.pinned_chats:
                            st.session_state.pinned_chats.remove(chat_name)
                            remove_pinned_chat(st.session_state.email,chat_name)
                        # 🔥 delete from UI
                        del st.session_state.chats[chat_name]
                        st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                        st.rerun()
        # 🔥 Rename Input (only shows when clicked)
        if "rename_target" in st.session_state:
            st.markdown("### ✏️ Rename Chat")
            new_name = st.text_input("Enter new name")
            if st.button("✅ Save New Name"):
                if new_name.strip():
                    new_name = new_name.strip()
                    if len(new_name) > 20:
                        st.error("❌ Maximum 20 characters allowed")
                        st.stop()
                    if new_name in st.session_state.chats:
                        st.error("❌ Chat name already exists")
                        st.stop()
                    old_name = st.session_state.rename_target
                    new_name = new_name[:20]
                    # DB update
                    rename_chat_in_db(st.session_state.email, old_name, new_name)
                    # UI update safely
                    st.session_state.chats[new_name] = st.session_state.chats.pop(old_name)
                    st.session_state.current_chat = new_name
                    # update pinned chat name
                    if old_name in st.session_state.pinned_chats:
                        st.session_state.pinned_chats.remove(old_name)
                        st.session_state.pinned_chats.append(new_name)
                        remove_pinned_chat(st.session_state.email,old_name)
                        save_pinned_chat(st.session_state.email,new_name)
                    del st.session_state.rename_target
                    st.rerun()
        st.markdown("---")
        # 🔽 OLD CODE CONTINUES
        st.write("👨‍💻 Developer: Harsh")
        st.write("🚀 Version: Ultra Pro v1")
        
        uploaded_file = st.file_uploader("📂 Upload File",type=["txt", "pdf", "png", "jpg", "jpeg"])
        file_type = ""
        if uploaded_file is not None:
            file_type = uploaded_file.name.split(".")[-1].lower()
        # 🔥 flag create
        if "file_processed" not in st.session_state:
            st.session_state.file_processed = False
        if uploaded_file is not None:
            # 🔒 File size limit (5MB)
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error("❌ File too large! Max 5MB allowed.")
                st.stop()
            # ✅ detect new file
            if uploaded_file.name != st.session_state.last_uploaded_filename:
                st.session_state.file_processed = False
                st.session_state.pdf_text = ""
                st.session_state.uploaded_image = None
                st.session_state.last_uploaded_filename = uploaded_file.name
            if uploaded_file is not None and not st.session_state.file_processed:
                content = ""
                file_type = uploaded_file.name.split(".")[-1].lower()
                allowed_mime = ["text/plain","application/pdf","image/png","image/jpeg"]
                if uploaded_file.type not in allowed_mime:
                    st.error("❌ Invalid file type detected")
                    st.stop()
                content = ""
            # ✅ IMAGE FILE
            if file_type in ["png", "jpg", "jpeg"]:
                try:
                    image = Image.open(uploaded_file)
                    image.verify()
                    uploaded_file.seek(0)
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", width="stretch")
                    st.session_state.uploaded_image = uploaded_file.getvalue()
                    st.session_state.last_uploaded_type = "image"
                except Exception:
                    st.error("❌ Invalid image")
                    st.stop()
            # ✅ TXT file
            elif file_type == "txt":
                st.session_state.last_uploaded_type = "txt"
                try:
                    content = uploaded_file.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    print("TXT Read Error:", e)
                    content = "Error reading TXT file"
            # ✅ PDF file
            elif file_type == "pdf":
                st.session_state.last_uploaded_type = "pdf"
                try:
                    content = extract_pdf_text(uploaded_file)

                    if not content.strip():
                        content = "⚠️ No readable text found (maybe scanned PDF)"

                    st.session_state.pdf_text = content

                except Exception as e:
                    content = f"❌ PDF Error: {str(e)}"
            else:
                content = "Unsupported file type"
            if "content" not in locals():
                content = ""
            content = content[:5000]
            st.success("✅ File/Image uploaded successfully!")
            st.session_state.file_processed = True
        # 🔥 reset when no file
        if uploaded_file is None:
            st.session_state.file_processed = False
        st.markdown("### 🧠 Commands")
        st.title("⚙ Settings")
        personality = st.selectbox("🧠 AI Personality",["Normal", "Funny", "Teacher", "Professional"])
        st.session_state.personality = personality
        st.session_state.internet_on = st.checkbox("🌐 Internet Access", value=True)
        selected_theme = st.selectbox("🎨 Select Theme", list(themes.keys()))
        if (selected_theme != st.session_state.theme and st.session_state.login):
            st.session_state.theme = selected_theme
            apply_theme()
            st.rerun()
        st.session_state.voice_enabled = st.checkbox( "🔊 Voice Output", value=st.session_state.voice_enabled)
        if st.button("🗑 Clear All Chat History"):
            conn_user, c_user = get_user_db(st.session_state.email)
            c_user.execute("DELETE FROM chat_history")
            conn_user.commit()
            conn_user.close()
            st.session_state.chats = {"Chat 1": []}
            st.session_state.current_chat = "Chat 1"
            st.success("Your chat deleted!")
        if st.button("🚪 Logout"):
            old_token = hash_token(st.session_state.get("session_token", ""))
            st.session_state.clear()
            st.session_state.login = False
            st.session_state.chats = {"Chat 1": []}
            st.session_state.current_chat = "Chat 1"
            st.session_state.stop_generation = False
            st.session_state.ai_generating = False
            c.execute(
                "DELETE FROM remembered_sessions WHERE session_token=?",
                (old_token,))
            conn.commit()
            st.success("👋 Logged out successfully")
            st.rerun()
    st.markdown(f"""
<p class='main-title'>
🔥 Welcome {st.session_state.first_name} 🚀
</p>
<p style='text-align:center; color:#000000; font-size:14px; font-weight:600;'>
📧 Logged in as: {st.session_state.email}
</p>
""", unsafe_allow_html=True)
    if (st.session_state.profile_pic and st.session_state.profile_pic.startswith("https://")):
        safe_pic = html.escape(st.session_state.profile_pic)
        st.markdown(f"""
        <div style="text-align:center; margin-top:10px;">
            <img src="{safe_pic}" 
            style="width:80px; height:80px; border-radius:50%; border:2px solid white;">
        </div>
        """, unsafe_allow_html=True)
    # ================= TYPING EFFECT =================
    current_chat = st.session_state.chats[st.session_state.current_chat]
    if (current_chat and current_chat[-1][1] == "Typing... ⏳" and not st.session_state.ai_generating):
        last_user_msg = st.session_state.get("regen_prompt") or st.session_state.chats[st.session_state.current_chat][-2][1]
        st.session_state.regen_prompt = None
        response_placeholder = st.empty()
        st.info("🤖 AI Thinking...")
        full_text = ""
        st.session_state.ai_generating = True
        try:
                display_text = ""
                for chunk in ask_ai_ollama(last_user_msg):
                    if st.session_state.stop_generation:
                        break
                    # only new streamed text
                    if chunk:
                        display_text += chunk
                        if len(display_text) > MAX_RESPONSE:
                            break
                    safe_stream = html.escape(display_text)
                    response_placeholder.markdown(f"""<div class="chat-ai">{safe_stream}<span class="cursor-blink">▌</span></div>""",unsafe_allow_html=True)
                full_text = display_text
                final_html = render_markdown_live(full_text)
                response_placeholder.markdown(f"""<div class="chat-ai markdown-body">{final_html}</div>""",unsafe_allow_html=True)
        except RuntimeError:
                pass
        st.markdown("""<script>ar chatContainer = document.querySelector('.chat-container');if(chatContainer){chatContainer.scrollTop = chatContainer.scrollHeight;}</script>""", unsafe_allow_html=True)
        if st.session_state.stop_generation and not full_text.strip():
            full_text = "⛔ Response stopped."
        st.session_state.chats[st.session_state.current_chat][-1] = ("AI", full_text)
        # ================= AUTO CHAT TITLE AFTER AI =================
        current_chat_name = st.session_state.current_chat
        chat_messages = st.session_state.chats[current_chat_name]
        # only first full conversation
        if current_chat_name.startswith("Chat") and len(chat_messages) >= 2:
            conversation_for_title = ""
            for sender, msg in chat_messages[:4]:
                conversation_for_title += f"{sender}: {msg}\n"
            title_prompt = conversation_for_title
            new_title = generate_chat_title(title_prompt)
            # avoid duplicate names
            original_title = new_title
            count = 1
            while new_title in st.session_state.chats:
                new_title = f"{original_title} {count}"
                count += 1
            # rename session
            st.session_state.chats[new_title] = st.session_state.chats.pop(current_chat_name)
            # rename DB
            rename_chat_in_db(st.session_state.email,current_chat_name,new_title)
            st.session_state.current_chat = new_title
        if full_text.strip():
            if full_text.strip():
                save_chat(st.session_state.email,st.session_state.current_chat,"AI",full_text)
            # ================= AUTO CONVERSATION SUMMARY =================
            chat_data = st.session_state.chats[st.session_state.current_chat]
            # every 20 messages
            if len(chat_data) >= 20:
                old_messages = chat_data[:-10]
                summary = generate_conversation_summary(old_messages)
                if summary:
                    st.session_state.conversation_summary = summary
                    save_summary(st.session_state.email,summary)
                    # keep only recent messages
                    st.session_state.chats[st.session_state.current_chat] = chat_data[-10:]
                    rewrite_chat(st.session_state.email,st.session_state.current_chat,st.session_state.chats[st.session_state.current_chat])
        if st.session_state.voice_enabled:
            speak_safe(full_text)
        st.session_state.ai_generating = False
        try:
            response.close()
        except NameError:
            pass
        except Exception as e:
            print("Response Close Error:", e)
        st.rerun()
    # Show Chat
    st.markdown("""<style>.chat-container{padding-bottom:120px;}</style>""", unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, (sender, msg) in enumerate(st.session_state.chats[st.session_state.current_chat]):
        col1, col2 = st.columns([8, 1])
        # LEFT SIDE (message)
        with col1:
            if sender == "You":
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:flex-end; align-items:center;">
                        <div class="chat-user">{html.escape(msg)}</div>
                        <div style="font-size:22px; margin-left:8px;">👤</div>
                    </div>
                    """,
                    unsafe_allow_html=True)
                # ✏️ Edit button
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.session_state.edit_text = msg
            else:
                if msg == "Typing... ⏳":
                    st.markdown(
                        """
                        <div style="display:flex; align-items:center;">
                            <div style="font-size:22px; margin-right:8px;">🤖</div>
                            <style>
                            .typing{
                            display:flex;
                            gap:6px;
                            padding:10px 14px;
                            background:rgba(255,255,255,0.08);
                            border-radius:16px;
                            width:max-content;
                            }
                            .typing span{
                            width:10px;
                            height:10px;
                            background:white;
                            border-radius:50%;
                            animation:bounce 1.2s infinite;
                            }
                            .typing span:nth-child(2){
                            animation-delay:0.2s;
                            }
                            .typing span:nth-child(3){
                            animation-delay:0.4s;
                            }
                            @keyframes bounce{
                            0%,80%,100%{
                            transform:scale(0.7);
                            opacity:0.5;
                            }
                            40%{
                            transform:scale(1);
                            opacity:1;
                            }
                            }
                            </style>
                            <div class="typing">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )   
                else:
                    if "```python" in msg:
                        clean_code = msg.replace("```python", "").replace("```", "").strip()
                        st.code(clean_code, language="python")
                    elif "```" in msg:
                        clean_code = msg.replace("```", "").strip()
                        st.code(clean_code)
                    else:
                        with st.container():
                            safe_msg = render_markdown_live(msg)
                            with st.container():
                                st.markdown(f"""<div class="chat-ai markdown-body">{safe_msg}</div>""",unsafe_allow_html=True)
                        # 🔄 Regenerate Button
                        if i == len(st.session_state.chats[st.session_state.current_chat]) - 1 and sender == "AI":
                            if st.button("🔄 Regenerate", key=f"regen_{i}"):
                                for j in range(i-1, -1, -1):
                                    if st.session_state.chats[st.session_state.current_chat][j][0] == "You":
                                        last_user = st.session_state.chats[st.session_state.current_chat][j][1]
                                        break
                                st.session_state.chats[st.session_state.current_chat].pop(i)
                                st.session_state.stop_generation = False
                                st.session_state.chats[st.session_state.current_chat].append(("AI", "Typing... ⏳"))
                                st.session_state.regen_prompt = last_user
                                st.rerun() 
        # RIGHT SIDE (delete button)
        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.chats[st.session_state.current_chat].pop(i)
                rewrite_chat(st.session_state.email,st.session_state.current_chat,st.session_state.chats[st.session_state.current_chat])
                st.rerun()

    # 🔥 Edit UI
    if "edit_index" in st.session_state:

        idx = st.session_state.edit_index
        chat_data = st.session_state.chats[st.session_state.current_chat]

        # Check index is still valid
        if 0 <= idx < len(chat_data):

            st.markdown("### ✏️ Edit Message")

            new_text = st.text_area(
                "Edit your message",
                value=chat_data[idx][1],
                key="edit_box"
            )

            if st.button("✅ Save Edit", key="save_edit_btn"):

                new_text = new_text.strip()

                if not new_text:
                    st.error("❌ Message cannot be empty")
                else:

                    st.session_state.chats[
                        st.session_state.current_chat
                    ][idx] = ("You", new_text)

                    # Remove messages after edited message
                    st.session_state.chats[
                        st.session_state.current_chat
                    ] = st.session_state.chats[
                        st.session_state.current_chat
                    ][:idx + 1]

                    rewrite_chat(
                        st.session_state.email,
                        st.session_state.current_chat,
                        st.session_state.chats[
                            st.session_state.current_chat
                        ]
                    )

                    # Add AI typing
                    st.session_state.chats[
                        st.session_state.current_chat
                    ].append(("AI", "Typing... ⏳"))

                    del st.session_state.edit_index

                    st.rerun()

        else:
            # Old/stale edit index
            del st.session_state.edit_index
    st.markdown("""</div>
    <script>
    var chatContainer = document.querySelector('.chat-container');
    if(chatContainer){chatContainer.scrollTop = chatContainer.scrollHeight;}
    </script>
    """, unsafe_allow_html=True)
    # Download
    if st.button("📄 Download as PDF"):
        pdf_path = export_chat_to_pdf(
            [
                {"sender": sender, "message": msg}
                for sender, msg in st.session_state.chats[st.session_state.current_chat]
            ],
            "chat.pdf"
        )
        with open(pdf_path, "rb") as f:
            st.download_button("⬇ Download PDF", f, file_name="chat.pdf")
    # ================= INPUT + VOICE SAME LINE =================
    st.markdown("""
    <style>
    .input-box{
    position:sticky;
    bottom:0;
    background:transparent;
    padding:10px;
    border-radius:20px;
    backdrop-filter:blur(16px);
    z-index:999;
    }
    /* MOBILE FLOATING INPUT */
    @media screen and (max-width:768px){
    .input-box{
    position:fixed !important;
    bottom:10px !important;
    left:10px !important;
    right:10px !important;
    padding:10px !important;
    background:rgba(15,23,42,0.92) !important;
    backdrop-filter:blur(18px) !important;
    border-radius:22px !important;
    box-shadow:0 8px 30px rgba(0,0,0,0.35);
    z-index:99999 !important;
    }
    /* Textarea */
    .input-box textarea{
    border-radius:18px !important;
    padding-right:60px !important;
    min-height:55px !important;
    font-size:15px !important;
    }
    /* Send button */
    .input-box button{
    height:48px !important;
    border-radius:50% !important;
    width:48px !important;
    min-width:48px !important;
    padding:0 !important;
    font-size:18px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    }
    /* Chat bottom spacing */
    .chat-container{
    padding-bottom:160px !important;
    }
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([7,1])
    with col1:
        def handle_submit():
            key = f"user_input_{st.session_state.input_key}"
            text = st.session_state.get(key, "")
            text = text.strip()[:MAX_USER_MESSAGE_CHARS]
            current_time = time.time()
            if current_time - st.session_state.ai_request_window > AI_REQUEST_WINDOW:
                st.session_state.ai_request_count = 0
                st.session_state.ai_request_window = current_time
            if st.session_state.ai_request_count >= MAX_AI_REQUESTS:
                st.error("🚫 AI request limit reached. Wait 1 minute.")
                return
            st.session_state.ai_request_count += 1
            if current_time < st.session_state.spam_block_until:
                remaining = int(st.session_state.spam_block_until - current_time)
                st.error(f"🚫 Too many messages. Wait {remaining} seconds.")
                return
            dangerous_patterns = ["select * from","drop table","--","<?php","<iframe","<script","javascript:","union select","delete from",]
            for bad in dangerous_patterns:
                if bad.lower() in text.lower():
                    st.error("❌ Dangerous input blocked")
                    return
            if current_time - st.session_state.last_msg_time < SPAM_MESSAGE_DELAY:
                st.session_state.spam_count += 1
                if st.session_state.spam_count >= MAX_SPAM_WARNINGS:
                    st.session_state.spam_block_until = (current_time + SPAM_BLOCK_TIME)
                    st.error("🚫 Spam detected. Wait 60 seconds.")
                    return
                st.error(f"⚠️ Please wait 3 seconds before sending another message ({st.session_state.spam_count}/5)")
                return
            st.session_state.spam_count = 0
            st.session_state.last_msg_time = current_time
            # 🔒 Prevent huge spam input
            if len(text) > 4000:
                st.error("❌ Message too long")
                return
            # 🔒 Block dangerous HTML/script
            blocked_patterns = ["<script","</script>","javascript:","onerror=","onload="]
            for pattern in blocked_patterns:
                if pattern in text.lower():
                    st.error("❌ Unsafe content detected")
                    return
            if text and text.strip():
                st.session_state.last_activity = time.time()
                remaining = MAX_CHAT_MESSAGES - len(st.session_state.chats[st.session_state.current_chat])
                if remaining <= 10:
                    st.warning(f"⚠ Only {remaining} messages left in this chat")
                if len(st.session_state.chats[st.session_state.current_chat]) >= 120:
                    st.error("❌ Chat limit reached. Create new chat.")
                    return
                # 🔥 RESET STOP BUTTON
                st.session_state.stop_generation = False
                # ✅ ADD USER MESSAGE
                st.session_state.chats[st.session_state.current_chat].append(("You", text))
                # ✅ ADD AI TYPING INSTANTLY
                st.session_state.chats[st.session_state.current_chat].append(("AI", "Typing... ⏳"))
                # ✅ SAVE USER MESSAGE
                save_chat(st.session_state.email,st.session_state.current_chat,"You",text)
                # ✅ CLEAR INPUT FAST
                st.session_state[key] = ""
                # ✅ INPUT KEY
                st.session_state.input_key += 1
                # 🔥 SHOW TYPING INSTANTLY FIRST
                st.rerun()
                # ================= MEMORY PROCESS BACKGROUND =================
                threading.Thread(target=lambda: [smart_save_memory(st.session_state.email,mem)for mem in extract_memory_with_ai(text)if len(mem) >= 8],daemon=True).start()
        st.text_area("💬 Ask anything...",key=f"user_input_{st.session_state.input_key}",height=70,placeholder="Type your message here...")
        st.button("➤", on_click=handle_submit)
        if st.button("⏹ Stop"):
            st.session_state.stop_generation = True
            st.warning("⛔ Generation stopped")
    with col2:
        if st.button("🎙"):
            voice = listen()
            st.session_state.last_activity = time.time()
            if voice not in ["No voice detected","Microphone error","Sorry, I did not understand"]:
                st.session_state.chats[st.session_state.current_chat].append(("You", voice))
                save_chat(st.session_state.email,st.session_state.current_chat,"You",voice)
                st.session_state.chats[st.session_state.current_chat].append(("AI", "Typing... ⏳"))
                st.rerun()
st.markdown("</div>", unsafe_allow_html=True)