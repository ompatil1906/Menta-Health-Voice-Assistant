import streamlit as st
from main import MentalHealthAssistant

# Initialize assistant and session states
assistant = MentalHealthAssistant()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful mental health assistant."}
    ]

if "listening" not in st.session_state:
    st.session_state.listening = False

# Streamlit UI Configuration
st.set_page_config(
    page_title="Mental Health Voice Assistant",
    page_icon=":brain:",
    layout="centered",
)

st.title("🎤 Mental Health Voice Assistant")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Control buttons
col1, col2, col3 = st.columns(3)
with col1:
    listen_btn = st.button("🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening")

with col2:
    last_response = next((m["content"] for m in reversed(st.session_state.messages) 
                        if m["role"] == "assistant"), "")
    speak_btn = st.button("🔊 Speak Response", disabled=not last_response)

with col3:
    stop_btn = st.button("⏹️ Stop Speaking")

# Handle button interactions
if listen_btn:
    st.session_state.listening = not st.session_state.listening

if st.session_state.listening:
    user_input = assistant.recognize_speech()
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        ai_response = assistant.generate_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
    
    st.session_state.listening = False
    st.rerun()

if speak_btn and last_response:
    if not assistant.speak_text(last_response):
        st.warning("Already speaking!")
    st.rerun()

if stop_btn:
    assistant.stop_speech()
    st.success("Speech stopped!")
    st.rerun()