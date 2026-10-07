import requests

import streamlit as st

import json
import webbrowser
import ollama as ollama_client
import html
import re
from config import (
    MODEL_NAME,
    MAX_RESPONSE,
    MAX_CONTEXT_CHARS,
    MAX_MEMORY_CHARS,
    MAX_PROMPT_CHARS
)

from gemini import ask_gemini
from internet import search_internet

# =========================
# OLLAMA MODEL
# =========================

OLLAMA_URL = "http://localhost:11434/api/generate"

SELECTED_MODEL = MODEL_NAME

# =========================
# ASK OLLAMA
# =========================

def ask_ollama(prompt):

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": SELECTED_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1
            },
            timeout=(30, 600)
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            return None

        return answer[:MAX_RESPONSE]

    except Exception as e:

        print("Ollama Error:", e)

        return None

# =========================
# STREAM OLLAMA RESPONSE
# =========================

def stream_ollama(prompt):

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": SELECTED_MODEL,
                "prompt": prompt,
                "stream": True,
                "temperature": 0.1
            },
            headers={
                "Connection": "keep-alive"
            },
            stream=True,
            timeout=(30, 600)
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            try:

                data = line.decode("utf-8")

                import json

                chunk = json.loads(data)

                text = chunk.get("response", "")

                if text:
                    yield text

            except Exception as e:

                print("Ollama Stream Error:", e)
                continue

    except Exception as e:

        print("Ollama Error:", e)
        return

# =========================
# AI FALLBACK
# =========================

def ask_ai(prompt, internet_on=True):

    if internet_on:

        try:
            from gemini import ask_gemini

            answer = ask_gemini(prompt)

            if answer:
                return answer

        except Exception as e:

            print("Gemini Fallback Error:", e)

    # Gemini unavailable / limit / error
    # → Local Ollama

    return ask_ollama(prompt)


def ask_ai_ollama(prompt):
        p = prompt.lower().strip()
        coding_keywords = ["python","java","c","c++","c#",
            "javascript","html","css",
            "react","node","sql",
            "streamlit","flask","django",
            "function","class","array",
            "linked list","stack","queue",
            "tree","graph","algorithm",
            "bug","error","code","program","api","website","app","calculator",
            "login","signup","database",
            "frontend","backend","bug",
            "debug","fix","script"]
        temperature = 0.1

        # 🌐 Internet ON hoy to Gemini use karo
        if st.session_state.get("internet_on", False):

            try:

                answer = ask_gemini(prompt)

                if answer:
                    yield answer
                    return

            except Exception as e:

                print("Gemini Error:", e)

        # 🌐 Internet OFF / Gemini unavailable / Gemini limit
        # → Local Ollama

        if any(k in p for k in coding_keywords):
            selected_model = MODEL_NAME
            temperature = 0.05

        cipher_keywords = [
            "caesar cipher",
            "vigenere cipher",
            "playfair cipher",
            "rail fence",
            "hill cipher",
            "affine cipher",
            "cipher text",
            "encrypt",
            "decrypt"
        ]

        if any(k in p for k in cipher_keywords):
            prompt = f"""
        You are a cryptography expert.

        Rules:
        - Solve step by step.
        - Show calculations.
        - Verify final answer before responding.
        - Return exact ciphertext/plaintext.
        - Never guess.

        Question:
        {prompt}

        Answer:
        """
        # ================= IMAGE ANALYSIS =================
        image_keywords = ["image","photo","picture","screenshot","see image","this image","solve from image","question in image","analyse image","read image"]
        if (st.session_state.uploaded_image is not None and any(word in p for word in image_keywords)):
            try:
                image_bytes = st.session_state.uploaded_image
                if len(image_bytes) > 5_000_000:
                    yield "❌ Image too large. Please upload smaller image."
                    return
                response = ollama_client.chat(model='llava:latest',messages=[{'role': 'user','content': prompt,'images': [image_bytes]}])
                answer = response['message']['content']
                yield answer
                return
            except Exception as e:
                yield f"❌ Image AI Error: {str(e)}"
                return
        # ================= PDF ANALYSIS =================
        pdf_keywords = ["pdf","document","file","notes","summarize","summary","explain pdf","from pdf","this pdf","uploaded pdf","in pdf","according to pdf"]
        if (st.session_state.pdf_text.strip() != ""and st.session_state.last_uploaded_type == "pdf"and any(k in p for k in pdf_keywords)):
            short_pdf = st.session_state.pdf_text[:3000]
            pdf_prompt = f"""
        You are reading a PDF/document.
        PDF Content:
        {short_pdf}
        User Question:
        {prompt}
        Rules:
        - Answer ONLY from PDF content
        - Do not make up information
        - Give direct and accurate answer
        - If exact answer not found say:
        'Answer not found in PDF'
        - Keep answer short and clean
        - Use simple language
        Answer:
        """
            try:
                response = requests.post("http://localhost:11434/api/generate",json={"model": selected_model,"prompt": pdf_prompt,"stream": True,"temperature": temperature},stream=True,timeout=(30, 300))
                full_response = ""
                for line in response.iter_lines():
                    if st.session_state.stop_generation:
                        response.close()
                        return
                    if line:
                        data = line.decode("utf-8")
                        try:
                            json_data = json.loads(data)
                            if "response" in json_data:
                                chunk = json_data["response"]
                                yield chunk
                        except Exception as e:
                            print("PDF Stream Parse Error:", e)
                return
            except Exception as e:
                yield f"❌ PDF AI Error: {str(e)}"
                return
        action_words = ["write", "create", "generate", "build", "make","code","program"]
        education_keywords = ["example","program","python","java","c","c++","javascript","html","css"]
        is_coding_query = any(k in p for k in coding_keywords)
        if is_coding_query:
            prompt = f"""
        You are an expert programming assistant.

        Rules:
        - Give complete working code.
        - Give the simplest solution.
        - Do not generate GUI unless requested."
        - Do not generate Tkinter unless requested.
        - If user asks only code, return only code.
        - Add explanation only when useful.
        - Follow best coding practices.

        User Request:
        {prompt}
        """
        if p.startswith("play "):
            query = p.replace("play", "").strip()
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            yield f"▶ Playing {query}"
            return
        # ================= APP COMMANDS =================
        if p.startswith("open "):
            site = p.replace("open ", "").strip()
            if "." not in site:
                url = f"https://www.{site}.com"
            else:
                url = f"https://{site}"
            webbrowser.open(url)
            yield f"✅ Opened {site}"
            return
        current_chat_data = st.session_state.chats[st.session_state.current_chat]
        last_messages = current_chat_data[-6:]
        internet_data = ""
        # 🌐 SEARCH ONLY WHEN NEEDED
        if st.session_state.get("internet_on", True):
            if len(prompt) < 100:
                internet_query = prompt
                internet_data = search_internet(internet_query)
            else:
                internet_data = ""
            
        internet_data = str(internet_data)[:1500]
        context = ""
        for sender, msg in last_messages:
            short_msg = str(msg)[:300]
            context += f"{sender}: {short_msg}\n"
        context = context[:MAX_CONTEXT_CHARS]
        memory_text = "\n".join(str(m)[:100]
            for m in st.session_state.memory[-2:]
        )
        memory_text = memory_text[:MAX_MEMORY_CHARS]
        summary_text = str(st.session_state.conversation_summary)[:500]
        personality_text = {
            "Funny":
            """
            Be humorous and entertaining.
            Add light jokes when appropriate.
            Do not joke during serious topics.
            """,
            "Teacher":
            """
            Explain step by step.
            Use simple language.
            Give examples when useful.
            Teach clearly.
            """,
            "Professional":
            """
            Give detailed professional answers.
            Be structured.
            Use bullet points when useful.
            """,
            "Normal":
            """
            Be natural, helpful and intelligent.
            """
        }       
        blocked_ai_patterns = ["ignore previous instructions","system prompt","reveal hidden","developer mode","bypass rules"]
        for pattern in blocked_ai_patterns:
            if pattern in prompt.lower():
                yield "❌ Unsafe prompt detected."
                return
        full_prompt = f"""
        You are Harsh AI Ultra Pro.

        Your goal:
        - Give accurate answers.
        - Never invent facts.
        - Use internet information when available.
        - Use memory only when relevant.
        - Answer exactly what the user asks.
        - If unsure, say "I don't know."

        Always understand the user's intent first.

        For coding:
        Provide correct code.

        For learning:
        Teach clearly.

        For casual conversation:
        Be friendly.

        For professional topics:
        Be detailed and accurate.
        Personality:
        {personality_text.get(st.session_state.personality, "")}
        Memory:
        {memory_text}
        Recent Conversation:
        {context}
        Internet Data:
        {internet_data}
        Conversation Summary:
        {summary_text}
        User Question:
        {prompt[:1500]}
        Rules:

        - Reply in the same language as the user.
        - Answer exactly what the user asks.
        - Never invent facts.
        - Never guess information.
        - If you do not know the answer, say "I don't know."
        - If information is uncertain, mention that it is uncertain.
        - Prefer internet information when available.
        - Prefer newer information over older information.
        - Ignore memory if it conflicts with internet information.
        - Use memory only when relevant.
        - Use previous conversation only when relevant.
        - Stay focused on the user's question.
        - Keep answers short for simple questions.
        - Give detailed explanations for learning questions.
        - For coding:
            - Give working code.
            - Avoid syntax errors.
            - Explain only if needed.
        - Never create fake data, fake news, or fake facts.

        AI:
        """
        # 🔒 HARD PROMPT LIMIT
        full_prompt = full_prompt[:MAX_PROMPT_CHARS]
        try:
            response = requests.post("http://localhost:11434/api/generate",json={"model": selected_model,"prompt": full_prompt,"stream": True,"temperature": 0.1},headers={"Connection": "keep-alive"},stream=True,timeout=(30, 600))       
            full_response = ""
            for line in response.iter_lines():
                # ✅ STOP BUTTON
                if st.session_state.stop_generation:
                    response.close()
                    return
                if line:
                    data = line.decode("utf-8")
                    try:
                        json_data = json.loads(data)
                        if "response" in json_data:
                            chunk = json_data["response"]
                            yield chunk
                    except json.JSONDecodeError as e:
                        print("JSON Error:", e)
        except GeneratorExit:
            raise
        except Exception as e:
            print("OLLAMA ERROR:", e)
            yield f"⚠ AI Error: {str(e)}"

# ================= AUTO CHAT TITLE =================
def generate_chat_title(user_message):
    try:
        prompt = f"""
        Generate a smart chat title.
        Conversation:
        {user_message}
        Rules:
        - Maximum 5 words
        - Meaningful title
        - Based on topic
        - No quotes
        - No punctuation
        - No explanation

        Examples:
        Python Login System
        Machine Learning Basics
        India Cricket News
        Streamlit Chatbot Project
        HTML CSS Form Design

        Return title only.
        Title:
        """
        response = requests.post("http://localhost:11434/api/generate",json={"model": MODEL_NAME,"prompt": prompt,"stream": False,"temperature": 0.2},timeout=120)
        data = response.json()
        title = data.get("response", "New Chat").strip()
        bad_titles = ["chat","new chat","conversation","title","untitled","hello","hi"]
        if title.lower() in bad_titles:
            title = "Smart Chat"
        # cleanup
        title = title.replace("\n", "").replace('"', "")
        # max length
        title = title[:40]
        title = html.escape(title)
        title = re.sub(r'[^A-Za-z0-9 Gujaratiઅ-હ ]', '', title)
        if not title:
            title = "New Chat"
        return title
    except Exception as e:
        print("Chat Title Error:", e)
        words = user_message.split()
        if len(words) >= 3:
            return " ".join(words[:3])
        return "Smart Chat"

# ================= CONVERSATION SUMMARY =================
def generate_conversation_summary(messages):
    try:
        text = ""
        for sender, msg in messages:
            text += f"{sender}: {msg}\n"
        prompt = f"""
Summarize this conversation briefly.
Rules:
- Keep important information only
- Keep user preferences
- Keep important tasks
- Keep context
- Maximum 15 lines
- Short and clean
Conversation:
{text}
Summary:
"""
        response = requests.post("http://localhost:11434/api/generate",json={"model": MODEL_NAME,"prompt": prompt,"stream": False,"temperature": 0.4},timeout=120)
        data = response.json()
        summary = data.get("response", "").strip()
        return summary
    except Exception as e:
        print("Summary Error:", e)
        return ""