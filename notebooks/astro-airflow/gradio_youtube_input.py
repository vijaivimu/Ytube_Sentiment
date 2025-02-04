import gradio as gr
from googleapiclient.discovery import build
from airflow.providers.postgres.hooks.postgres import PostgresHook
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# YouTube API key
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Function to create the input_youtubeid table if it doesn't exist
def create_input_youtubeid_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS input_youtubeid (
        id SERIAL PRIMARY KEY,
        video_id VARCHAR(50) UNIQUE,
        date_added TIMESTAMP DEFAULT NOW()
    );
    """
    postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()

# Function to validate YouTube video ID
def validate_youtube_id(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            return True, response['items'][0]['snippet']['title']  # Video exists
        else:
            return False, None  # Video ID not found
    except Exception as e:
        return False, str(e)

# Function to insert video ID into PostgreSQL
def insert_video_id(video_id):
    create_input_youtubeid_table()  # Ensure the table exists before inserting
    postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    insert_query = """
    INSERT INTO input_youtubeid (video_id, date_added)
    VALUES (%s, NOW())
    ON CONFLICT (video_id) DO NOTHING;  -- Prevent duplicate entries
    """
    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_query, (video_id,))
            conn.commit()

# Gradio Interface Function
def submit_video_id(video_id):
    is_valid, info = validate_youtube_id(video_id)
    if is_valid:
        insert_video_id(video_id)
        return f"✅ Video ID '{video_id}' added successfully! Video Title: {info}"
    else:
        return f"❌ Invalid Video ID: {info if info else 'Video not found'}"

# Create Gradio Interface
iface = gr.Interface(
    fn=submit_video_id,
    inputs=gr.Textbox(label="Enter YouTube Video ID"),
    outputs="text",
    title="YouTube Video ID Submission",
    description="Enter a valid YouTube video ID. The system will validate and store it for processing."
)

# Launch the Gradio UI
iface.launch()
