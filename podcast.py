import streamlit as st
from googleapiclient.discovery import build
import re

YOUTUBE_API_KEY = "AIzaSyCXF_4_9F4FDzN5u9WEuNQZFkcNzH6mYVs"

def get_youtube_podcasts(query, max_results=3):
    """
    Fetches top YouTube videos based on a search query.
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results
    )
    response = request.execute()

    video_data = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        video_data.append((title, f"https://www.youtube.com/watch?v={video_id}", video_id))

    return video_data

def extract_mood_from_report(report_text):
    """
    Extracts the mood/emotional state from the generated mental health report.
    """
    mood_keywords = {
        "happy": ["positive", "happy", "content", "joyful"],
        "sad": ["sad", "depressed", "down", "low"],
        "stressed": ["stressed", "overwhelmed", "tense", "pressure"],
        "anxious": ["anxious", "worried", "nervous", "fearful"],
        "calm": ["calm", "relaxed", "peaceful", "mindful"]
    }

    report_text = report_text.lower()
    for mood, keywords in mood_keywords.items():
        if any(keyword in report_text for keyword in keywords):
            return mood
    return "general"  # Default mood if no match

def display_podcasts():
    """
    Displays YouTube podcast recommendations based on the generated mental health report.
    """
    st.title("🎙 Podcast Recommendations")

    if "analysis_result" in st.session_state and st.session_state.analysis_result:
        mood = extract_mood_from_report(st.session_state.analysis_result)

        mood_queries = {
            "happy": "motivational mental health podcast",
            "sad": "uplifting mental health talks",
            "stressed": "guided meditation for stress relief",
            "anxious": "anxiety relief guided meditation",
            "calm": "peaceful mindfulness meditation",
            "general": "best mental health podcast"
        }

        query = mood_queries.get(mood, "mental health podcast")
        podcasts = get_youtube_podcasts(query)

        st.subheader(f"🎧 Recommended Podcasts for '{mood.capitalize()}' Mood:")
        for title, link, video_id in podcasts:
            st.markdown(f"### {title}")
            st.video(f"https://www.youtube.com/embed/{video_id}")  # Embed video
            st.markdown("---")  # Separator
    else:
        st.warning("⚠️ Please generate your Mental Health Report first!")

