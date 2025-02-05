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
    initial_sidebar_state="collapsed",
)

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
            border-radius: 12px,;
            width: 100%;
            border: 1px solid #444444;
        }

        .stSlider {
            background-color: #121212;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎤 **Mental Health Assistant**")
st.markdown("💬 *Talk to your AI companion for emotional support*")

if st.session_state.show_history:
        st.subheader("📜 Chat History")
        chat_history = st.session_state.assistant.get_chat_history()
        for entry in chat_history:
            with st.chat_message("user"):
                st.markdown(entry['user_input'])
            with st.chat_message("assistant"):
                st.markdown(entry['ai_response'])

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
    if st.button("📜 Show Chat History" if not st.session_state.show_history else "❌ Hide History"):
        st.session_state.show_history = not st.session_state.show_history

col1, col2, col3 = st.columns(3)
with col1:
    listen_btn = st.button(
        "🎙️ Start Listening" if not st.session_state.listening else "🔴 Stop Listening"
    )
with col2:
    stop_btn = st.button("⏹️ Stop Speaking")
with col3:
    detect_btn = st.button("🧠 Generate Report")

if listen_btn:
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        st.info("🎤 Listening... Speak now!")
        user_input = st.session_state.assistant.recognize_speech()
        if user_input:
            st.session_state.listening = False
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Typing..."):
                    ai_response = st.session_state.assistant.process_user_input(user_input)
                    time.sleep(1)
                    st.markdown(ai_response)
            st.rerun()

if stop_btn:
    st.session_state.assistant.stop_speech()
    st.success("🔇 Speech stopped.")
    st.rerun()

if detect_btn:
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    user_id = st.session_state.user_id
    report = st.session_state.assistant.generate_report_for_user(user_id)
    if report:
        st.session_state.show_report = True
        st.session_state.analysis_result = report
    else:
        st.warning("No conversation history detected.")
    st.rerun()

if st.session_state.show_report:
    with st.expander("📊 **Mental Health Report**", expanded=True):
        st.markdown(f'<div class="report-box">{st.session_state.analysis_result}</div>', unsafe_allow_html=True)

    # Display Report
if st.session_state.show_report and "report" in st.session_state:
    st.subheader("📄 Mental Health Report:")
    st.markdown(st.session_state.report)

    # Generate PDF Report
    def generate_pdf(report_text):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            normal_style = ParagraphStyle("Normal", parent=styles['Normal'], fontName="Helvetica", fontSize=12, leading=14, spaceAfter=12, spaceBefore=6)
            for line in report_text.split('\n'):
                line = line.strip()
                paragraph = Paragraph(line, normal_style)
                story.append(paragraph)

            doc.build(story)
            buffer.seek(0)
            return buffer

    pdf_buffer = generate_pdf(st.session_state.analysis_result)
    st.download_button(label="📥 Download PDF", data=pdf_buffer, file_name="mental_health_report.pdf", mime="application/pdf")
