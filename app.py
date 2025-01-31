import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import speech_recognition as sr
import pyttsx3
import threading
import time

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Voice-Enabled ChatBot",
    page_icon=":brain:",
    layout="centered",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# State to control listening and stopping AI response
if "listening" not in st.session_state:
    st.session_state.listening = False

if "stop_response" not in st.session_state:
    st.session_state.stop_response = False

# Global variable to control the speech thread
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
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            st.warning("Speech recognition service is unavailable.")
            return "Speech recognition service is unavailable."

# Function to speak out the response
def speak_text(text):
    def run_speech():
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)  # Adjust speed
        engine.say(text)
        engine.runAndWait()

    # Start the speech thread
    st.session_state.speech_thread = threading.Thread(target=run_speech, daemon=True)
    st.session_state.speech_thread.start()

# Function to stop the speech
def stop_speech():
    if st.session_state.speech_thread and st.session_state.speech_thread.is_alive():
        # Forcefully stop the speech thread
        st.session_state.stop_response = True
        st.session_state.speech_thread.join(timeout=0.1)  # Wait for the thread to finish
        st.session_state.speech_thread = None
        st.warning("AI response stopped by user.")

# Display chatbot title
st.title("🎤 Voice-Enabled ChatBot")

# Display all previous chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        st.markdown(content)

# Button to toggle listening state
if st.button("🎙️ Start Listening" if not st.session_state.listening else "🔊 Stop Listening"):
    st.session_state.listening = not st.session_state.listening

# Button to stop AI response
if st.button("⏹️ Stop AI Response"):
    stop_speech()

# Start listening and processing user prompt
if st.session_state.listening:
    user_prompt = recognize_speech()
    if user_prompt:
        # Append user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.chat_message("user").markdown(f"**You:** {user_prompt}")

        # Get response from Gemini-Pro
        gemini_response = st.session_state.chat_session.send_message(user_prompt)

        # Append AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": gemini_response.text})

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

        # Check if the stop response flag is not set before speaking
        if not st.session_state.stop_response:
            # Speak out the response
            speak_text(gemini_response.text)
        else:
            st.warning("AI response stopped by user.")

        # Reset stop response after speaking or after stopping
        st.session_state.stop_response = False

        # Stop listening after response is given
        st.session_state.listening = False