from pymongo import MongoClient
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import pytz  

client = MongoClient(os.getenv("MONGO_URI"))
db = client["mental_health"]
moods_collection = db["mood_logs"]

# Define local timezone (change it if needed)
local_timezone = pytz.timezone("Asia/Kolkata") 

def extract_mood_from_report(report_text):
    """Extracts the mood from the generated mental health report."""
    mood_keywords = {
        "Stressed": ["stressed", "Stressed","overwhelmed", "tense", "pressure", "burnout"],
        "Sad": ["sad", "depressed", "down", "low"],
        "Happy": ["positive", "happy", "content", "joyful"],
        "Anxious": ["anxious", "worried", "nervous", "fearful"],
        "Calm": ["calm", "relaxed", "peaceful", "mindful"],
        "Neutral": ["neutral"]
    }

    report_text = report_text.lower()
    detected_mood = "Neutral" 

    for mood, keywords in mood_keywords.items():
        if any(keyword in report_text for keyword in keywords):
            detected_mood = mood
            break 

    return detected_mood 


def store_mood_in_db(detected_mood):
    mood_entry = {
        "mood": detected_mood.lower(),
        "timestamp": datetime.utcnow()  # Store timestamp in UTC
    }
    moods_collection.insert_one(mood_entry)

def get_all_moods():
    moods = list(moods_collection.find({}, {"_id": 0, "mood": 1, "timestamp": 1}))

    for mood in moods:
        utc_time = mood["timestamp"]
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        mood["timestamp"] = local_time.strftime("%Y-%m-%d %H:%M:%S")  # Convert to readable format

    return moods

def display_moodtracker():
    if "analysis_result" in st.session_state and st.session_state.analysis_result:
        mood = extract_mood_from_report(st.session_state.analysis_result)
        store_mood_in_db(mood)  
        st.markdown(f"Your mood: **{mood.capitalize()}**")
    else:
        st.warning("⚠ Please generate your Mental Health Report first!")
    
    mood_records = get_all_moods()
    if mood_records:
        df = pd.DataFrame(mood_records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[['timestamp', 'mood']]

        #colors and symbols
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
