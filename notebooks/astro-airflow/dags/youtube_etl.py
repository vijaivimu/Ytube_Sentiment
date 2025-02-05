# Import necessary libraries for the ETL pipeline

# Airflow libraries
from airflow import DAG
from airflow.decorators import task, dag
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

# For YouTube API interaction
from googleapiclient.discovery import build

# For data manipulation
import pandas as pd

# For environment variable management
from dotenv import load_dotenv
import os

# For text preprocessing
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re
import emoji

# Load environment variables
load_dotenv()

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),  # Set to the desired start date
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ✅ Proper indentation within the DAG context
with DAG(
    'youtube_comment_extractor',
    default_args=default_args,
    description='A DAG to extract YouTube comments daily',
    schedule_interval='@daily',  # Runs daily
    catchup=False
) as dag:

    @task
    def create_table():
        create_table_query = """
        CREATE TABLE IF NOT EXISTS youtube_comments (
            id SERIAL PRIMARY KEY,
            comment_id VARCHAR(50),
            video_id VARCHAR(50),
            author VARCHAR(255),
            comment TEXT,
            cleaned_comment TEXT,
            likes INTEGER,
            published_at TIMESTAMP,
            sentiment VARCHAR(20),
            UNIQUE (comment_id, video_id)  -- Composite key to avoid duplicates
        );
        """
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
                conn.commit()

    @task
    def fetch_video_ids():
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        fetch_query = "SELECT video_id FROM input_youtubeid;"
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(fetch_query)
                video_ids = [row[0] for row in cursor.fetchall()]
        return video_ids

    @task
    def get_comments(video_id):
        API_KEY = os.getenv('YOUTUBE_API_KEY')
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()

        comments = []
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_id = item['snippet']['topLevelComment']['id']  # Fetch comment ID

            comments.append({
                'Comment_ID': comment_id,
                'Video_ID': video_id,
                'Author': comment['authorDisplayName'],
                'Comment': comment['textDisplay'],
                'Likes': comment['likeCount'],
                'Published At': comment['publishedAt'],
                'Sentiment': None  # Placeholder for sentiment analysis
            })

        return comments  # Return list of comments (dicts)

    @task
    def preprocess_comments(comments_list):
        stop_words = ENGLISH_STOP_WORDS  # Built-in stopwords from scikit-learn

        def clean_text(text):
            text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
            text = emoji.replace_emoji(text, replace='')  # Remove emojis
            text = ' '.join([word for word in text.split() if word.lower() not in stop_words])  # Remove stop words
            return text

        for comment in comments_list:
            comment['Cleaned_Comment'] = clean_text(comment['Comment'])
        return comments_list

    @task
    def load_to_postgres(preprocessed_comments):
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')

        insert_query = """
        INSERT INTO youtube_comments (comment_id, video_id, author, comment, cleaned_comment, likes, published_at, sentiment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (comment_id, video_id) DO NOTHING;  -- Ignore duplicates
        """

        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                for comment in preprocessed_comments:
                    cursor.execute(insert_query, (
                        comment['Comment_ID'],
                        comment['Video_ID'],
                        comment['Author'],
                        comment['Comment'],
                        comment['Cleaned_Comment'],
                        comment['Likes'],
                        comment['Published At'],
                        comment['Sentiment']  # Currently None
                    ))
                conn.commit()

    # ✅ Ensure these are indented within the DAG context
    create_table_task = create_table()
    video_ids_task = fetch_video_ids()

    # Dynamic Task Mapping
    comments_task = get_comments.expand(video_id=video_ids_task)
    preprocessed_comments_task = preprocess_comments.expand(comments_list=comments_task)
    load_data_task = load_to_postgres.expand(preprocessed_comments=preprocessed_comments_task)

    # ✅ Task dependencies
    create_table_task >> video_ids_task >> comments_task >> preprocessed_comments_task >> load_data_task