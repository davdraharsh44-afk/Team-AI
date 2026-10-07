import html
import markdown
import streamlit as st

from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

# =========================
# MARKDOWN RENDERING
# =========================

def render_markdown_live(text):

    try:

        return markdown.markdown(
            text,
            extensions=[
                FencedCodeExtension(),
                TableExtension(),
                "nl2br"
            ]
        )

    except Exception:

        return html.escape(text)

# ================= THEMES =================
themes = {"Pink": ("#FF4FD8", "#0f2027"),"Dark Cyan": ("#00FFD1", "#0E1117"),"Neon Green": ("#39FF14", "#000000"),"Royal Blue": ("#4F9DFF", "#1e3c72"),"Sunset": ("#FF7E5F", "#2c3e50"),"Purple Dream": ("#C77DFF", "#240046"),"Gold": ("#FFD700", "#1a1a1a"),"Red Fire": ("#FF3131", "#1b0000"),"Ocean": ("#00BFFF", "#000428"),"Lime": ("#A4FF00", "#111111"),"Teal": ("#00FFC6", "#0f2027"),"Orange Blast": ("#FF8C00", "#1a1a1a"),"White Minimal": ("#111111", "#ffffff")}
def apply_theme():
    main_color, bg = themes[st.session_state.theme]

    st.markdown(f"""<style>               
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
*{{
font-family:'Poppins',sans-serif;
}}
/* Markdown Styling */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3{{
margin-top:10px;
margin-bottom:10px;
font-weight:700;
}}
.markdown-body code{{
background:#111827;
padding:2px 6px;
border-radius:6px;
color:#00ffcc;
}}
.markdown-body pre{{
background:#0f172a;
padding:16px;
border-radius:14px;
overflow-x:auto;
border:1px solid #1e293b;
margin-top:10px;
margin-bottom:10px;
}}
.markdown-body pre code{{
background:transparent !important;
color:#ffffff !important;
font-size:14px;
line-height:1.6;
}}
.markdown-body code{{
background:#111827;
padding:3px 7px;
border-radius:6px;
color:#00ffcc;
font-size:14px;
}}
.markdown-body ul{{
padding-left:20px;
}}
.markdown-body table{{
width:100%;
border-collapse:collapse;
margin-top:10px;
}}
.markdown-body th,
.markdown-body td{{
border:1px solid #ccc;
padding:8px;
}}
/* FIX TOP HEADER */
header[data-testid="stHeader"] {{
    background: #e5e7eb !important;
    color: black !important;
    border-bottom: 1px solid #cbd5e1;
}}
/* FIX TOOLBAR */
div[data-testid="stToolbar"] {{
    background: #e5e7eb !important;
    border-radius: 10px;
    padding: 5px;
}}
/* Background */
body{{
background: linear-gradient(-45deg,#0f172a,#1e293b,#020617,#111827);
background-size:400% 400%;
animation:gradientBG 15s ease infinite;
font-family:'Poppins',sans-serif;
}}
/* Main App */
.stApp{{
background: transparent;
}}
section[data-testid="stSidebar"]{{
background:#ffffff !important;
backdrop-filter:blur(16px);
border-right:1px solid #d1d5db;
padding-top:10px;
}}
/* Sidebar Search Box */
section[data-testid="stSidebar"] input{{
background:white !important;
color:black !important;
border:2px solid black !important;
border-radius:12px !important;
padding:10px !important;
}}
/* Placeholder */
section[data-testid="stSidebar"] input::placeholder{{
color:#666666 !important;
}}              
/* Sidebar Buttons */
section[data-testid="stSidebar"] button{{
border-radius:14px !important;
transition:0.2s ease;
border:none !important;
}}
section[data-testid="stSidebar"] button:hover{{
transform:translateX(5px);
background:linear-gradient(90deg,#2563eb,#7c3aed) !important;
}}
/* Title */
.main-title{{
text-align:center;
font-size:42px;
font-weight:800;
background:linear-gradient(90deg,#60a5fa,#a855f7,#ec4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:8px;
animation:fadeIn 1s ease;
}}
/* 🔥 INPUT FIX */
input, textarea{{
background:white !important;
color:black !important;
border:2px solid #cbd5e1 !important;
border-radius:18px !important;
padding:12px !important;
}}
/* Placeholder */
textarea::placeholder{{
color:#666666 !important;
}}
/* Labels */
label {{
    color: {main_color} !important;
    font-weight: 600;
}}
/* Checkbox */
.stCheckbox label {{
    color: {main_color} !important;
}}
/* Buttons */
button{{
border:none !important;
border-radius:16px !important;
background:linear-gradient(135deg,#2563eb,#7c3aed) !important;
color:white !important;
font-weight:600 !important;
transition:0.25s ease;
box-shadow:0 6px 18px rgba(37,99,235,0.25);
}}
button:hover{{
transform:translateY(-2px) scale(1.02);
box-shadow:0 10px 24px rgba(124,58,237,0.35);
}}
.chat-user{{
background:linear-gradient(135deg,#2563eb,#1d4ed8);
color:white;
padding:14px 18px;
border-radius:22px 22px 4px 22px;
margin:4px 0;
margin-left:auto;
max-width:75%;
font-size:15px;
box-shadow:0 8px 20px rgba(37,99,235,0.3);
animation:fadeIn 0.3s ease;
backdrop-filter:blur(12px);
}}
.chat-ai{{
background:#ffffff;
color:#000000;
padding:14px 18px;
border-radius:22px 22px 22px 4px;
margin:4px 0;
max-width:75%;
font-size:15px;
border:1px solid #d1d5db;
backdrop-filter:blur(14px);
box-shadow:0 8px 30px rgba(0,0,0,0.12);
animation:fadeIn 0.3s ease;
display:inline-block;
line-height:1.6;
white-space:pre-wrap;
word-wrap:break-word;
overflow-wrap:anywhere;
}}
/* Streaming Cursor */
.cursor-blink{{
animation:blink 1s infinite;
font-weight:bold;
}}
@keyframes blink{{
0%{{opacity:1;}}
50%{{opacity:0;}}
100%{{opacity:1;}}
}}
/* Animation */
@keyframes fadeIn{{
from{{
opacity:0;
transform:translateY(10px);
}}
to{{
opacity:1;
transform:translateY(0);
}}
}}
/* Animations */
@keyframes gradientBG {{
0% {{background-position:0% 50%;}}
50% {{background-position:100% 50%;}}
100% {{background-position:0% 50%;}}
}}
/* Scroll */
::-webkit-scrollbar {{
width:6px;
}}
::-webkit-scrollbar-thumb {{
background:{main_color};
border-radius:10px;
}}
hr {{display: none !important;}}
</style>""", unsafe_allow_html=True)
st.markdown("""
<style>
/* ✅ KEEP LAPTOP UI PERFECT */
.block-container{
max-width:1200px;
margin:auto;
padding-top:1rem !important;
padding-bottom:5rem !important;
}
/* Desktop */
.chat-user,
.chat-ai{
max-width:70%;
word-wrap:break-word;
overflow-wrap:anywhere;
white-space:pre-wrap;
}
/* MOBILE ONLY */
@media screen and (max-width:768px){
/* Main spacing */
.block-container{
padding-left:8px !important;
padding-right:8px !important;
padding-top:0.5rem !important;
padding-bottom:7rem !important;
}
/* Title */
.main-title{
font-size:24px !important;
line-height:1.3 !important;
margin-top:10px !important;
}
/* Chat bubbles */
.chat-user,
.chat-ai{
max-width:95% !important;
font-size:14px !important;
padding:12px !important;
border-radius:18px !important;
line-height:1.5 !important;
}
/* AI bubble */
.chat-ai{
margin-left:2px !important;
}
/* User bubble */
.chat-user{
margin-right:2px !important;
}
/* Input textarea */
textarea{
font-size:16px !important;
border-radius:16px !important;
padding:12px !important;
min-height:60px !important;
}
/* Buttons */
button{
height:44px !important;
border-radius:14px !important;
font-size:14px !important;
}
/* Sidebar */
section[data-testid="stSidebar"]{
width:85% !important;
}
/* Uploaded image */
img{
border-radius:16px !important;
}
/* Code blocks */
pre{
font-size:13px !important;
border-radius:14px !important;
overflow-x:auto !important;
}
/* Tables */
table{
font-size:12px !important;
}
/* Reduce top gap */
[data-testid="stHeader"]{
height:50px !important;
}
/* Bottom input area */
.input-box{
position:fixed !important;
bottom:0 !important;
left:0 !important;
right:0 !important;
padding:10px !important;
background:rgba(15,23,42,0.95) !important;
backdrop-filter:blur(12px) !important;
border-top:1px solid rgba(255,255,255,0.1);
z-index:9999 !important;
}
/* Chat container */
.chat-container{
padding-bottom:140px !important;
}
/* Make columns compact */
[data-testid="column"]{
padding:2px !important;
}
}
/* TABLET */
@media screen and (min-width:769px) and (max-width:1024px){
.chat-user,
.chat-ai{
max-width:80% !important;
}
}
</style>
""", unsafe_allow_html=True)
