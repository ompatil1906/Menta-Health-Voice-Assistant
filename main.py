import os
import speech_recognition as sr
import pyttsx3
import threading
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class MentalHealthAssistant:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.speech_thread = None

    def recognize_speech(self):
        """Capture and convert speech to text"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                return recognizer.recognize_google(audio, language="en-US")
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                return None

    def generate_response(self, messages):
        """Get AI response from Groq"""
        response = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def speak_text(self, text):
        """Convert text to speech in a background thread"""
        if self.speech_thread and self.speech_thread.is_alive():
            return False
        
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
            
        self.speech_thread = threading.Thread(target=_speak, daemon=True)
        self.speech_thread.start()
        return True

    def stop_speech(self):
        """Stop current speech output"""
        self.engine.stop()
        if self.speech_thread:
            self.speech_thread.join(timeout=1)
        return True