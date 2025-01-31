import os
import streamlit as st  # type: ignore
from dotenv import load_dotenv  # type: ignore
import google.generativeai as gen_ai  # type: ignore
import speech_recognition as sr  # Speech-to-text
import pyttsx3  # Text-to-speech (offline)
import threading  # To prevent run loop errors
import time  # For delay in stopping the speech

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
    st.session_state.messages = []  # Stores all chat messages

# State to control listening and stopping AI response
if "listening" not in st.session_state:
    st.session_state.listening = False  # Initially, not listening

if "stop_response" not in st.session_state:
    st.session_state.stop_response = False  # Initially, response is not stopped

# Function to recognize speech input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio,language="en-US")  # Convert speech to text
            return text
        except sr.UnknownValueError:
            st.warning("Sorry, I couldn't understand that.")
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            st.warning("Speech recognition service is unavailable.")
            return "Speech recognition service is unavailable."

# Function to speak out the response (avoiding run loop errors)
def speak_text(text):
    # Check if stop response is triggered
    if st.session_state.stop_response:
        st.warning("AI response stopped by user.")
        return

    def run_speech():
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)  # Adjust speed
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run_speech, daemon=True).start()

# Function to stop the speech
def stop_speech():
    st.session_state.stop_response = True

# Display chatbot title
st.title("🎤 Voice-Enabled ChatBot")

# Button to toggle listening state
if st.button("🎙️ Start Listening" if not st.session_state.listening else "🔊 Stop Listening"):
    st.session_state.listening = not st.session_state.listening  # Toggle state

# Button to stop AI response
if st.button("⏹️ Stop AI Response"):
    stop_speech()

# Start listening and processing user prompt
if st.session_state.listening:
    user_prompt = recognize_speech()
    if user_prompt:
        st.chat_message("user").markdown(f"**You:** {user_prompt}")

        # Get response from Gemini-Pro
        gemini_response = st.session_state.chat_session.send_message(user_prompt)

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
        st.session_state.stop_response = False  # Reset after response

        # Stop listening after response is given
        st.session_state.listening = False  # Reset listening state after response
