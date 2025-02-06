import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Custom theme and styling
st.set_page_config(layout="wide", page_title="Mental Health Dashboard")

# Modern blue & white theme
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-blue: #1E88E5;
            --light-blue: #90CAF9;
            --white: #FFFFFF;
            --light-gray: #F5F5F5;
        }
        
        /* Background and text colors */
        .stApp {
            background-color: var(--white);
            color: #2C3E50;
        }
        
        /* Buttons styling */
        .stButton > button {
            background-color: var(--primary-blue);
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Cards/containers styling */
        .css-1r6slb0 {
            background-color: var(--white);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Metrics styling */
        .metric-card {
            background-color: var(--light-blue);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Dashboard layout
def create_dashboard():
    # Header
    col1, col2 = st.columns([2,1])
    with col1:
        st.title("🧠 Mental Health Analytics Dashboard")
    with col2:
        st.button("Start New Session")

    # Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Sessions", "28", "+3")
            st.markdown("</div>", unsafe_allow_html=True)
    with m2:
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Mood Score", "7.5", "+0.5")
            st.markdown("</div>", unsafe_allow_html=True)
    with m3:
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Response Time", "1.2s", "-0.3s")
            st.markdown("</div>", unsafe_allow_html=True)
    with m4:
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Active Users", "12", "+2")
            st.markdown("</div>", unsafe_allow_html=True)

    # Main content
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("Recent Conversations")
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.assistant.messages:
                if message["role"] != "system":
                    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                        st.markdown(message["content"])

    with col2:
        st.subheader("Quick Actions")
        st.button("🎙️ Start Voice Chat")
        st.button("📊 Generate Report")
        st.button("📥 Export Data")
        
        # Mood Tracker
        st.subheader("Daily Mood Tracker")
        mood = st.slider("How are you feeling today?", 1, 10, 5)
        if st.button("Save Mood"):
            st.success("Mood recorded!")

    # Bottom section
    st.subheader("Analytics")
    tab1, tab2 = st.tabs(["Mood Trends", "Usage Statistics"])
    
    with tab1:
        # Sample mood trend chart using Plotly
        dates = [datetime.now() - timedelta(days=x) for x in range(7)]
        mood_scores = [7, 6, 8, 7, 9, 8, 7]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=mood_scores, mode='lines+markers',
                                line=dict(color='#1E88E5', width=2),
                                marker=dict(size=8, color='#90CAF9')))
        fig.update_layout(
            title="Weekly Mood Trends",
            xaxis_title="Date",
            yaxis_title="Mood Score",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Initialize dashboard
if __name__ == "__main__":
    create_dashboard()
