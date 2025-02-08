import streamlit as st
import time
from main import MentalHealthAssistant 
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from io import BytesIO

st.set_page_config(
    page_title="Mental Health Voice Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if "assistant" not in st.session_state:
    st.session_state.assistant = MentalHealthAssistant()
if "listening" not in st.session_state:
    st.session_state.listening = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "show_history" not in st.session_state:
    st.session_state.show_history = False
if "show_report" not in st.session_state:
    st.session_state.show_report = False
if "last_processed_input" not in st.session_state:
    st.session_state.last_processed_input = ""
if "show_info" not in st.session_state:
    st.session_state.show_info = False
st.markdown("""
    <style>
        .chat-container {
            display: flex;
            margin-bottom: 10px;
        }
        .chat-container.user {
            justify-content: flex-end;
        }
        .chat-container.assistant {
            justify-content: flex-start;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .chat-bubble.user {
            background-color: #DCF8C6;
            text-align: right;
        }
        .chat-bubble.assistant {
            background-color: #E3E3E3;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# Left sidebar for chat history
with st.sidebar:
    st.header("Chat History")
    if st.session_state.show_history:
        chat_history = st.session_state.assistant.get_chat_history()
        for entry in chat_history:
            with st.chat_message("user"):
                st.markdown(entry['user_input'])
            with st.chat_message("assistant"):
                st.markdown(entry['ai_response'])
    else:
        st.info("History is currently hidden. Enable it using the toggle in the main view.")

# Main content area
st.title("🎤 Mental Health Assistant")
st.markdown("💬 Talk to your AI companion for emotional support")

# Info and history controls
col1, col2 = st.columns([0.85, 0.15])
with col1:
    if st.session_state.show_info:
        with st.expander("ℹ️ About Bot", expanded=True):
            st.markdown("""
                🎤 **Voice activated mental health companion**  
                🧠 Detects mental wellness and emotional state  
                🔊 Speaks responses aloud for natural interaction  
                💬 Chat interface for text-based communication  
                📊 Generates detailed mental health reports  
                📥 Export your session history as PDF  
            """)
with col2:
    st.button("ℹ️ Toggle Info", on_click=lambda: st.session_state.update(show_info=not st.session_state.show_info))
    st.button("📜 Toggle History", on_click=lambda: st.session_state.update(show_history=not st.session_state.show_history))

# Display chat messages
for message in st.session_state.assistant.messages:
    if message["role"] == "system":
        continue

    role_class = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if message["role"] == "user" else "🤖"

    st.markdown(f"""
        <div class="chat-container {role_class}">
            <div class="chat-bubble {role_class}">
                <b>{avatar}</b> {message["content"]}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Chat input and processing
if prompt := st.chat_input("Type your message or click microphone to speak..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing..."):
            response = st.session_state.assistant.process_user_input(prompt)
            st.markdown(response)

# Voice controls at bottom
st.markdown("---")
cols = st.columns(3)
with cols[0]:
    if st.button("🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening"):
        st.session_state.listening = not st.session_state.listening
        if st.session_state.listening:
            user_input = st.session_state.assistant.recognize_speech()
            if user_input:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_input)
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Analyzing..."):
                        response = st.session_state.assistant.process_user_input(user_input, is_voice=True)
                        st.markdown(response)
                st.session_state.listening = False
                st.rerun()
with cols[1]:
    if st.button("⏹️ Stop Speaking"):
        st.session_state.assistant.stop_speech()
with cols[2]:
    if st.button("📊 Generate Report"):
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        report = st.session_state.assistant.generate_report_for_user(st.session_state.user_id)
        if report:
            st.session_state.show_report = True
            st.session_state.analysis_result = report
            st.rerun()

# Report generation section
if st.session_state.show_report:
    with st.expander("📊 Mental Health Report", expanded=True):
        st.markdown(f'<div class="report-box">{st.session_state.analysis_result}</div>', unsafe_allow_html=True)
        
        def generate_pdf(report_text):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            style = ParagraphStyle('Custom', parent=styles['Normal'], 
                                 fontSize=12, leading=14, textColor=colors.black)
            for line in report_text.split('\n'):
                p = Paragraph(line, style)
                story.append(p)
            doc.build(story)
            buffer.seek(0)
            return buffer

        pdf_buffer = generate_pdf(st.session_state.analysis_result)
        st.download_button("📥 Download PDF", data=pdf_buffer, 
                         file_name="mental_health_report.pdf", 
                         mime="application/pdf")
        