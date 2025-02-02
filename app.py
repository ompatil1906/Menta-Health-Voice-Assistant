import streamlit as st
import time
from main import MentalHealthAssistant  # Ensure the MentalHealthAssistant class is imported

# Initialize session state and assistant
if "assistant" not in st.session_state:
    st.session_state.assistant = MentalHealthAssistant()

if "listening" not in st.session_state:
    st.session_state.listening = False

# Configure Streamlit page
st.set_page_config(
    page_title="Mental Health Voice Assistant",
    page_icon=":brain:",
    layout="centered",
)

st.title("🎤 Mental Health Voice Assistant")

# Display chat history
for message in st.session_state.assistant.messages:
    if message["role"] == "system":
        continue  # Skip system messages
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Control buttons
col1, col2, col3 = st.columns(3)
with col1:
    listen_btn = st.button("🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening")
with col2:
    stop_btn = st.button("⏹️ Stop Speaking")
with col3:
    detect_btn = st.button("🧠 Detect Mental Health")  # New button

# Handle UI interactions
if listen_btn:
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        st.rerun()  # Rerun to update the UI

if st.session_state.listening:
    user_input = st.session_state.assistant.recognize_speech()
    if user_input:
        st.session_state.listening = False
        with st.chat_message("user"):
            st.markdown(user_input)
        
        ai_response = st.session_state.assistant.process_user_input(user_input)
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.rerun()  # Rerun to update the UI

if stop_btn:
    st.session_state.assistant.stop_speech()
    st.rerun()  # Rerun to update the UI

if detect_btn:
    st.session_state.analysis_result = st.session_state.assistant.detect_mental_health()

if "analysis_result" in st.session_state and st.session_state.analysis_result:
    with st.expander("📊 Mental Health Analysis Report", expanded=True):
        st.markdown(st.session_state.analysis_result)

