import speech_recognition as sr
import pyttsx3
import threading
import streamlit as st

# =========================
# SPEECH TO TEXT
# =========================

def speech_to_text():

    try:

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:

            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)

        return text

    except Exception as e:

        print("Speech Recognition Error:", e)

        return ""


# =========================
# TEXT TO SPEECH
# =========================

def text_to_speech(text):

    try:

        engine = pyttsx3.init()

        engine.say(text)

        engine.runAndWait()

    except Exception as e:

        print("Text to Speech Error:", e)

def speak_safe(text):
    if len(text) > 1000:
        text = text[:1000]
    def run():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print("Voice Error:", e)
    threading.Thread(target=run, daemon=True).start()

def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            # Background noise adjust
            r.adjust_for_ambient_noise(source, duration=1)
            # Listen with limits
            audio = r.listen(source, timeout=7, phrase_time_limit=12)
            # Try English
            try:
                return r.recognize_google(audio, language="en-IN")
            except Exception as e:
                print("English Voice Error:", e)
            # Try Hindi
            try:
                return r.recognize_google(audio, language="hi-IN")
            except Exception as e:
                print("Hindi Voice Error:", e)
            # Try Gujarati
            try:
                return r.recognize_google(audio, language="gu-IN")
            except Exception as e:
                print("Gujarati Voice Error:", e)
            return "Sorry, I did not understand"
    except sr.WaitTimeoutError:
        return "No voice detected"
    except Exception:
        return "Microphone error"