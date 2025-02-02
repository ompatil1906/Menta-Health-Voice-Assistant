import streamlit as st
import time
from main import MentalHealthAssistant  # Ensure MentalHealthAssistant is imported

# ✅ Set page configuration FIRST
st.set_page_config(
    page_title="Mental Health Voice Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ✅ Initialize session state properly
if "assistant" not in st.session_state:
    st.session_state.assistant = MentalHealthAssistant()
if "listening" not in st.session_state:
    st.session_state.listening = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

# ✅ Now you can set your custom CSS
st.markdown("""
    <style>
        body {background-color: #121212; color: white;}
        .stButton > button {border-radius: 10px; font-size: 18px; padding: 10px; width: 100%; transition: 0.3s;}
        .stButton > button:hover {background-color: #1DB954; color: white;}
        .stChatMessage {border-radius: 10px; padding: 10px; margin-bottom: 10px;}
        .stChatMessage-user {background-color: #1E1E1E; color: white;}
        .stChatMessage-assistant {background-color: #252525; color: #1DB954;}
        .report-box {background-color: #181818; padding: 10px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🎤 **Mental Health Voice Assistant**")

# Display Chat History with Avatars
for message in st.session_state.assistant.messages:
    if message["role"] == "system":
        continue  # Skip system messages
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Sidebar for additional info
with st.sidebar:
    st.subheader("ℹ️ About BuddyBot")
    st.markdown("👋 *A friendly AI companion for mental health support.*")
    st.markdown("🎙️ *Voice recognition enabled*")
    st.markdown("💬 *Chat & detect emotional health*")
    st.markdown("🔊 *Speaks responses aloud*")

# Control Buttons (Grid Layout)
col1, col2, col3 = st.columns(3)

with col1:
    listen_btn = st.button(
        "🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening",
        key="listen"
    )
with col2:
    stop_btn = st.button("⏹️ Stop Speaking", key="stop")
with col3:
    detect_btn = st.button("🧠 Detect Mental Health", key="detect")

# Handle Button Actions
if listen_btn:
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        st.info("🎤 Listening... Speak now!")
        user_input = st.session_state.assistant.recognize_speech()
        if user_input:
            st.session_state.listening = False
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            # Process AI Response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🤖 Typing..."):
                    ai_response = st.session_state.assistant.process_user_input(user_input)
                    time.sleep(1)  # Simulate typing delay
                    st.markdown(ai_response)
            
            st.rerun()  # Refresh UI

if stop_btn:
    st.session_state.assistant.stop_speech()
    st.success("🔇 Speech stopped.")
    st.rerun()

if detect_btn:
    with st.spinner("🧠 Analyzing Mental Health..."):
        st.session_state.analysis_result = st.session_state.assistant.detect_mental_health()
        time.sleep(2)  # Simulate processing time
    st.rerun()

# Show Mental Health Report if available
if st.session_state.analysis_result:
    with st.expander("📊 **Mental Health Analysis Report**", expanded=True):
        st.markdown(f'<div class="report-box">{st.session_state.analysis_result}</div>', unsafe_allow_html=True)
