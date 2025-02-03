import streamlit as st
import time
from main import MentalHealthAssistant 

st.set_page_config(
    page_title="Mental Health Voice Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "assistant" not in st.session_state:
    st.session_state.assistant = MentalHealthAssistant()
if "listening" not in st.session_state:
    st.session_state.listening = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

st.markdown("""
    <style>
        body {background-color: #000000; color: white;}  /* Overall page background set to black */
        
        .stButton > button {
            border-radius: 12px; 
            font-size: 18px; 
            padding: 15px; 
            width: 100%; 
            transition: 0.4s; 
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }
        
        .stButton > button:hover {
            background-color: #708090;  
            color: white;
        }
        
        .stChatMessage {
            border-radius: 12px; 
            padding: 12px; 
            margin-bottom: 12px;
        }
        
        .stChatMessage-user {
            background-color: #333333; 
            color: white;
        }
        
        .stChatMessage-assistant {
            background-color: #2d2d2d; 
            color: #1DB954;
        }
        
        .report-box {
            background-color: #333333;  /* Report box background set to white */
            color: white;  /* Text color for the report box */
            padding: 15px; 
            border-radius: 12px; 
            border: 1px solid #444444;
        }

        .stSlider {
            background-color: #121212;
        }
    </style>
""", unsafe_allow_html=True)


# Title and Subtitle
st.title("🎤 **Voice-Enabled Mental Health Assistant**")
st.markdown("**Talk to your AI Assistant for a healthier mind**")

# Display Chat History with Avatars
for message in st.session_state.assistant.messages:
    if message["role"] == "system":
        continue  # Skip system messages
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Sidebar for additional info and support
with st.sidebar:
    st.subheader("ℹ️ About Bot")
    st.markdown("🎤 *Voice activated mental health companion*")
    st.markdown("🧠 *Detects mental wellness and emotional state*")
    st.markdown("🔊 *Speaks responses aloud, fostering interaction*")
    st.markdown("💬 *Easy to use: Chat with AI for mental health support*")

# Control Buttons (Centered Layout)
col1, col2, col3 = st.columns([2, 2, 2])

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
                with st.spinner(" Typing..."):
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


