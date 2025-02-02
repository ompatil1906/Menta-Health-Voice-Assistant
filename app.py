import streamlit as st
import time
from main import MentalHealthAssistant

# Initialize session state and assistant
if "assistant" not in st.session_state:
    st.session_state.assistant = MentalHealthAssistant()

if "listening" not in st.session_state:
    st.session_state.listening = False

# Configure Streamlit page
st.set_page_config(
    page_title="Mental health Voice Assistant",
    page_icon=":brain:",
    layout="centered",
)

st.title("🎤 Mental Health Voice Assistant")

# Display chat history
for message in st.session_state.assistant.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Control buttons
col1, col2, col3 = st.columns(3)
with col1:
    listen_btn = st.button("🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening")
with col2:
    stop_btn = st.button("⏹️ Stop Speaking")

# Handle UI interactions
if listen_btn:
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        st.rerun()

if st.session_state.listening:
    user_input = st.session_state.assistant.recognize_speech()
    if user_input:
        st.session_state.listening = False
        with st.chat_message("user"):
            st.markdown(user_input)
        
        ai_response = st.session_state.assistant.process_user_input(user_input)
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.rerun()



if stop_btn:
    st.session_state.assistant.stop_speech()
    st.rerun()

# Handle listening status display
if st.session_state.listening:
    st.info("Listening... Speak now.")
    # Add small delay to prevent constant rerun
    time.sleep(0.1)
    st.rerun()