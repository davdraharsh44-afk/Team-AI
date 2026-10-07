import os

import google.generativeai as genai

from dotenv import load_dotenv

# =========================
# LOAD GEMINI API
# =========================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# =========================
# GEMINI MODEL
# =========================

model = None

if GEMINI_API_KEY:

    model = genai.GenerativeModel(
        "gemini-flash-latest"
    )

# =========================
# ASK GEMINI
# =========================

def ask_gemini(prompt):

    if model is None:
        return None

    try:

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:

        print("Gemini Error:", e)

        return None