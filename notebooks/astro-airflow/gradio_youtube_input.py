import gradio as gr
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

# Load environment variables
load_dotenv()

# YouTube API key
API_KEY = os.getenv('YOUTUBE_API_KEY')

# PostgreSQL connection details
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Function to fetch all stored video sentiment data (Runs every time UI updates)
def fetch_sentiment_data():
    query = """
    SELECT i.video_id, i.video_title, 
           COUNT(c.sentiment) FILTER (WHERE c.sentiment = 'positive') AS positive_count,
           COUNT(c.sentiment) FILTER (WHERE c.sentiment = 'negative') AS negative_count
    FROM input_youtubeid i
    LEFT JOIN youtube_comments c ON i.video_id = c.video_id
    GROUP BY i.video_id, i.video_title;
    """
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    
    if not results:
        return pd.DataFrame(columns=["Video ID", "Title", "Sentiment"])
    
    # Process data into a DataFrame
    data = []
    for video_id, title, pos_count, neg_count in results:
        total = (pos_count or 0) + (neg_count or 0)
        if total > 0:
            positive_percentage = (pos_count / total) * 100
            negative_percentage = (neg_count / total) * 100
            sentiment_summary = f"{positive_percentage:.1f}% Positive | {negative_percentage:.1f}% Negative"
        else:
            sentiment_summary = "⏳ Sentiment analysis in progress, try later."
        
        data.append([video_id, title, sentiment_summary])
    
    return pd.DataFrame(data, columns=["Video ID", "Title", "Sentiment"])

# Function to validate YouTube video ID and get title
def validate_youtube_id(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            title = response['items'][0]['snippet']['title']
            return True, title  # Video exists, return title
        else:
            return False, None  # Video ID not found
    except Exception as e:
        return False, str(e)

# Function to insert video ID and title into PostgreSQL
def insert_video_id(video_id, video_title):
    insert_query = """
    INSERT INTO input_youtubeid (video_id, video_title, date_added)
    VALUES (%s, %s, NOW())
    ON CONFLICT (video_id) DO NOTHING;  -- Prevent duplicate entries
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_query, (video_id, video_title))
    conn.close()

# Function to fetch sentiment analysis results for a given video_id
def get_sentiment_summary(video_id):
    query = """
    SELECT COUNT(*) FILTER (WHERE sentiment = 'positive') AS positive_count,
           COUNT(*) FILTER (WHERE sentiment = 'negative') AS negative_count
    FROM youtube_comments WHERE video_id = %s;
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (video_id,))
            result = cursor.fetchone()

    if result:
        positive_count, negative_count = result
        total = positive_count + negative_count
        if total == 0:
            return "⏳ Sentiment analysis in progress, try later."

        positive_percentage = (positive_count / total) * 100
        negative_percentage = (negative_count / total) * 100

        return f"📊 {positive_percentage:.1f}% Positive | {negative_percentage:.1f}% Negative"
    return "⏳ Sentiment analysis in progress, try later."

# Function to handle video submission
def submit_video_id(video_id):
    is_valid, video_title = validate_youtube_id(video_id)
    
    if is_valid:
        # Insert video into database
        insert_video_id(video_id, video_title)
        
        # Get sentiment analysis results
        sentiment_result = get_sentiment_summary(video_id)
        
        # Refresh sentiment table
        new_sentiment_table = fetch_sentiment_data()
        
        return f"✅ Video '{video_id}' added successfully!\n📺 Title: {video_title}\n{sentiment_result}", new_sentiment_table
    else:
        return f"❌ Invalid Video ID: {video_title if video_title else 'Video not found'}", fetch_sentiment_data()

# **Gradio Interface**
with gr.Blocks() as iface:
    gr.Markdown("# 🎬 YouTube Video ID Submission & Sentiment Analysis")
    
    with gr.Row():
        video_input = gr.Textbox(label="Enter YouTube Video ID")
        submit_button = gr.Button("Submit")
        refresh_button = gr.Button("🔄 Refresh Data")

    sentiment_output = gr.Textbox(label="Status", interactive=False)
    
    # **✅ Table always fetches fresh sentiment data**
    sentiment_table_display = gr.Dataframe(
        value=fetch_sentiment_data, headers=["Video ID", "Title", "Sentiment"], interactive=False
    )

    # **Submit button triggers video insertion & refreshes table**
    submit_button.click(
        submit_video_id, inputs=[video_input], outputs=[sentiment_output, sentiment_table_display]
    )

    # **Refresh button fetches latest sentiment data**
    refresh_button.click(
        fetch_sentiment_data, outputs=[sentiment_table_display]
    )

# Launch Gradio UI
iface.launch()