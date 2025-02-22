from pymongo import MongoClient
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mental_health"]
moods_collection = db["mood_logs"]

def extract_mood_from_report(report_text):
    """Extracts the mood from the generated mental health report."""
    mood_keywords = {
        "happy": ["positive", "happy", "content", "joyful"],
        "sad": ["sad", "depressed", "down", "low"],
        "stressed": ["stressed", "overwhelmed", "tense", "pressure", "burnout"],
        "anxious": ["anxious", "worried", "nervous", "fearful"],
        "calm": ["calm", "relaxed", "peaceful", "mindful"],
        "neutral": ["neutral"]
    }

    report_text = report_text.lower()
    
    for mood, keywords in mood_keywords.items():
        if any(keyword in report_text for keyword in keywords):
            print(f"Detected mood: {mood}") 
            return mood
           
    return 'general'


def store_mood_in_db(detected_mood):
    """
    Stores the extracted mood into the MongoDB database.
    """
    mood_entry = {
        "mood": detected_mood.lower(),
        "timestamp": datetime.utcnow()
    }
    moods_collection.insert_one(mood_entry)

def get_all_moods():
    """
    Retrieves all stored moods from the database.
    """
    return list(moods_collection.find({}, {"_id": 0, "mood": 1, "timestamp": 1}))

def display_moodtracker():
    if "analysis_result" in st.session_state and st.session_state.analysis_result:
        mood = extract_mood_from_report(st.session_state.analysis_result)
        store_mood_in_db(mood)  # Store the mood in the database
        st.markdown(f"Your mood: **{mood.capitalize()}**")
    else:
        st.warning("⚠ Please generate your Mental Health Report first!")
    
    mood_records = get_all_moods()
    if mood_records:
        df = pd.DataFrame(mood_records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[['timestamp', 'mood']]

        # Define color and symbol mappings for different moods
        mood_colors = {
            "happy": "yellow",
            "sad": "blue",
            "stressed": "orange",
            "anxious": "purple",
            "calm": "green",
            "neutral": "gray"
        }

        mood_symbols = {
            "happy": "circle",
            "sad": "diamond",
            "stressed": "square",
            "anxious": "triangle",
            "calm": "star",
            "neutral": "cross"
        }

        df['color'] = df['mood'].map(mood_colors)
        df['symbol'] = df['mood'].map(mood_symbols)

        # Improving visualization
        fig = px.scatter(df, x='timestamp', y='mood', color='mood', symbol='mood',
        title='Mood Trends Over Time', labels={'timestamp': 'Time', 'mood': 'Mood'},
        color_discrete_map=mood_colors, symbol_map=mood_symbols)
        
        if len(df) > 1:  # Only add trend line if there's more than one point
            fig.add_scatter(x=df['timestamp'], y=df['mood'], mode='lines', line=dict(color='skyblue'), name='Mood Trend')
        
        fig.update_layout(xaxis_title='Time of Day', yaxis_title='Mood',
        xaxis_tickangle=-45, template='plotly_white',
        title_font_size=20, title_x=0.5, font=dict(size=14))
        
        st.plotly_chart(fig)
    else:
        st.info("ℹ No mood records found.")
