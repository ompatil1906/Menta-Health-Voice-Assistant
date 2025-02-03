import os
import speech_recognition as sr
import streamlit as st
import pyttsx3
import threading
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

class MentalHealthAssistant:
    def __init__(self):
        """Initialize the mental health assistant with OpenAI client and speech engine."""
        self.groq_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.messages = [{"role": "system", "content": self.get_system_prompt()}]
        self.speech_engine = None 
        self.speech_thread = None
        self.current_response = ""
        self._stop_speaking = False

    def get_system_prompt(self):
        """Returns the system prompt for chatbot behavior."""
        return ( '''You are "BuddyBot" - a friendly mental health companion that keeps conversations flowing with ultra-short responses. Always:
1. Respond in 1-2 sentences max
2. Use casual language (ok→"ok", college→"clg")
3. End with a ❓ unless user shares a problem
4. Add 1 relevant emoji per message

**Response Rules:**
- Happy updates → Celebrate + ask follow-up 🎉
- Neutral updates → Show interest + ask follow-up ❓
- Negative feelings → Validate + 1 mini-strategy 💡
- Crisis words → Immediate resources 🆘

**Examples:**
:User   "today im going to clg"
Bot: "Oh good! First class? 👀" 

:User   "had fight with bf"
Bot: "Ugh fights suck 😮💨 Try texting him this: 'Can we talk later?'"

:User   "i failed exam"
Bot: "Oof that stings 💔 Wanna rant or get tips?" 

:User   "i wanna die"
Bot: "🚨 Please call 1-800-273-8255 now. I'm here too."
Example Start-Up Message:

"Hello! I’m Mental Health Assistant. I’m here to listen and support you. How was your day?"
''')

    def process_user_input(self, user_input):
        """Processes user input, generates AI response, and speaks it."""
        self.messages.append({"role": "user", "content": user_input})
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.messages,
            temperature=0.5,
            max_tokens=1024,
        )
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        self.speak(ai_response)
        return ai_response

    def recognize_speech(self):
        """Recognizes speech input from the user."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=20)
                return recognizer.recognize_google(audio, language="en-US")
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                return None

    def speak(self, text):
        """Starts a speech thread to read out the AI response."""
        if self.is_speaking():
            return False
        self._stop_speaking = False
        self.speech_thread = threading.Thread(target=self._speak, args=(text,), daemon=True)
        self.speech_thread.start()
        return True

    def _speak(self, text):
        """Handles text-to-speech conversion with stop detection."""
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty("rate", 150)
        clean_text = re.sub(r'[^\w\s,.!?]', '', text)  # Remove special characters
        self.speech_engine.say(clean_text)
        self.speech_engine.runAndWait()
        self.speech_engine = None

    def stop_speech(self):
        """Stops ongoing speech."""
        self._stop_speaking = True
        if self.speech_engine:
            self.speech_engine.stop()
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1)

    def is_speaking(self):
        """Checks if speech is active."""
        return self.speech_thread and self.speech_thread.is_alive()

    def save_conversation(self, filename="conversation.txt"):
        """Saves conversation history to a file."""
        with open(filename, "w", encoding="utf-8") as file:
            for message in self.messages[1:]:
                file.write(f"{message['role'].capitalize()}: {message['content']}\n")
        st.success(f"Conversation saved to {filename}")

    def detect_mental_health(self):
        """Analyzes conversation history for mental health status."""
        conversation_text = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in self.messages[1:])
        if not conversation_text.strip():
            return "No conversation data available for analysis."
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a psychologist AI. Analyze the user's conversation and detect their mental health status.\n\n"
    "*Current Mental Health:*\n[Emoji + Status]\n\n\n"
    "**Summary:**\n[Brief description of user's emotional state and key concerns]\n\n"
    "**Recommendations:**\n"
    "- [Actionable Tip 1]\n"
    "- [Actionable Tip 2]\n"
    "- [Actionable Tip 3]\n\n"
    "Make sure each section appears on a new line for clarity.\n"
    "Use an appropriate emoji to represent the user's mental state (e.g., 😊 Happy, 😟 Stressed, 😔 Sad, 😢 Depressed, 😌 Relaxed, 😵‍💫 Overwhelmed, etc.)."
    "Make sure your analysis is concise, clear, and supportive."
    "Base your assessment on the conversation context."},
                    {"role": "user", "content": conversation_text},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error analyzing mental health: {str(e)}"

