import os
import speech_recognition as sr
import streamlit as st
import pyttsx3
import threading
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



class MentalHealthAssistant:
    def __init__(self):
        self.groq_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.messages = [{"role": "system", "content": "You are a helpful mental health assistant."}]

        self.speech_engine = None 
        self.speech_thread = None
        self.current_response = ""
        self._stop_speaking = False
   
    def process_user_input(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        response = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=self.messages,
            temperature=0.5,
            max_tokens=1024,
        )
        
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        self.current_response = ai_response
        return ai_response

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now.")
            recognizer.adjust_for_ambient_noise(source)
            try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio, language="en-US")
                    return text
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                    return None

    def _speak(self, text):
        """Handle text-to-speech with engine reinitialization"""
        self._stop_speaking = False
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty("rate", 150)
        
        # Add event callbacks for proper cleanup
        def on_start(name):
            if self._stop_speaking:
                self.speech_engine.stop()

        def on_word(name, location, length):
            if self._stop_speaking:
                self.speech_engine.stop()

        self.speech_engine.connect('started-utterance', on_start)
        self.speech_engine.connect('started-word', on_word)
        
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()
        self.speech_engine = None  # Clean up engine after use

    def speak_response(self, text):
        """Start speaking response thread"""
        if self.is_speaking():
            return False
        
        self._stop_speaking = False
        self.speech_thread = threading.Thread(
            target=self._speak, 
            args=(text,),
            daemon=True
        )
        self.speech_thread.start()
        return True

    def stop_speech(self):
        """Stop current speech"""
        self._stop_speaking = True
        if self.speech_engine:
            self.speech_engine.stop()
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1)

    def is_speaking(self):
        """Check if currently speaking"""
        return self.speech_thread and self.speech_thread.is_alive()