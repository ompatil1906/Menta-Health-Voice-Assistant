import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import threading
import time

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Mental health Voice Assistant",
    page_icon=":brain:",
    layout="centered",
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set up Groq client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful mental health assistant."}
    ]

if "listening" not in st.session_state:
    st.session_state.listening = False

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "speech_thread" not in st.session_state:
    st.session_state.speech_thread = None

# Function to recognize speech input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-US")
            return text
        except sr.UnknownValueError:
            st.warning("Sorry, I couldn't understand that.")
            return ""
        except sr.RequestError:
            st.warning("Speech recognition service is unavailable.")
            return ""

# Text-to-speech function
def speak_text(text):
    def run_speech():
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.say(text)
        engine.runAndWait()
    
    if st.session_state.speech_thread and st.session_state.speech_thread.is_alive():
        st.warning("Already speaking!")
        return
    
    st.session_state.speech_thread = threading.Thread(target=run_speech, daemon=True)
    st.session_state.speech_thread.start()

# Function to stop speech
def stop_speech():
    if st.session_state.speech_thread and st.session_state.speech_thread.is_alive():
        engine = pyttsx3.init()
        engine.stop()
        st.session_state.speech_thread.join()
        st.success("Speech stopped!")

# Display UI
st.title("🎤 Mental Health Voice Assistant")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Control buttons layout
col1, col2, col3 = st.columns(3)
with col1:
    listen_btn = st.button("🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening")

with col2:
    speak_btn = st.button("🔊 Speak Response", disabled=not st.session_state.last_response)

with col3:
    stop_btn = st.button("⏹️ Stop Speaking")

# Handle listening toggle
if listen_btn:
    st.session_state.listening = not st.session_state.listening

# Process voice input
if st.session_state.listening:
    user_input = recognize_speech()
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=st.session_state.messages,
            temperature=0.5,
            max_tokens=1024,
        )

        ai_response = response.choices[0].message.content
        
        # Store response and update chat
        st.session_state.last_response = ai_response
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)

    st.session_state.listening = False

# Handle speech requests
if speak_btn and st.session_state.last_response:
    speak_text(st.session_state.last_response)

if stop_btn:
    stop_speech()