import os
import speech_recognition as sr
import streamlit as st
import pyttsx3
import threading
from openai import OpenAI
from dotenv import load_dotenv
import re  # Import regex for text cleaning

load_dotenv()

class MentalHealthAssistant:
    def __init__(self):
        self.groq_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.messages = [{"role": "system", "content": '''You are "BuddyBot" - a friendly mental health companion that keeps conversations flowing with ultra-short responses. Always:
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
'''}]

        self.speech_engine = None 
        self.speech_thread = None
        self.current_response = ""
        self._stop_speaking = False
   
    def process_user_input(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.messages,
            temperature=0.5,
            max_tokens=1024,
        )
        
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        self.current_response = ai_response
        
        # Automatically speak the response
        self.speak(ai_response)
        
        return ai_response

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now.")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=20)
                text = recognizer.recognize_google(audio, language="en-US")
                return text
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                return None

    def _speak(self, text):
        """Handle text-to-speech with engine reinitialization"""
        self._stop_speaking = False
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty("rate", 150)
        
        # Clean the text to remove emojis and symbols
        clean_text = self.clean_text(text)

        # Add event callbacks for proper cleanup
        def on_start(name):
            if self._stop_speaking:
                self.speech_engine.stop()

        def on_word(name, location, length):
            if self._stop_speaking:
                self.speech_engine.stop()

        self.speech_engine.connect('started-utterance', on_start)
        self.speech_engine.connect('started-word', on_word)
        
        self.speech_engine.say(clean_text)
        self.speech_engine.runAndWait()
        self.speech_engine = None  # Clean up engine after use

    def clean_text(self, text):
        """Remove emojis and non-alphanumeric characters from the text"""
        # Regex to remove emojis and special characters
        return re.sub(r'[^\w\s,.!?]', '', text)

    def speak(self, text):
        """Start speaking response directly"""
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

    def save_conversation(self, filename="conversation.txt"):
        """Save the full conversation to a text file"""
        with open(filename, "w",encoding="utf-8") as file:
            for message in self.messages[1:]:
                role = message["role"]
                content = message["content"]
                file.write(f"{role.capitalize()}: {content}\n")
        st.success(f"Conversation saved to {filename}")

    def detect_mental_health(self):
        """Analyzes conversation using LLM and detects mental health status."""
        filename = "conversation.txt"
        
        # Save conversation first
        with open(filename, "w", encoding="utf-8") as file:
            for message in self.messages[1:]:  # Skip system prompt
                role = message["role"]
                content = message["content"]
                file.write(f"{role.capitalize()}: {content}\n")

        # Read the conversation for analysis
        with open(filename, "r", encoding="utf-8") as file:
            conversation_text = file.read()

        if not conversation_text.strip():
            return "No conversation data available for analysis."

        # Debug: Check what is being sent to the LLM
        print("🔍 Conversation sent to LLM:\n", conversation_text)

        try:
            # Send conversation to LLM for mental health analysis
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": 
                        "You are a psychologist AI. Analyze the user's conversation and detect their mental health."
                        "Provide a clear mental health status, a brief summary, and 3 actionable recommendations."
                    },
                    {"role": "user", "content": conversation_text},
                ],
                temperature=0.7,
                max_tokens=300,
            )

            analysis_result = response.choices[0].message.content.strip()

            if not analysis_result:
                return "⚠️ No response from LLM. Please try again."

            print("✅ AI Analysis Output:\n", analysis_result)  # Debugging output

            return analysis_result

        except Exception as e:
            print(f"❌ Error in mental health analysis: {str(e)}")
            return f"⚠️ Error analyzing mental health: {str(e)}"

