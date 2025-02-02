# Import necessary libraries for the ETL pipeline

# Airflow libraries
from airflow import DAG
from airflow.decorators import task
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
import re
from nltk.corpus import stopwords
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
            author VARCHAR(255),
            comment TEXT,
            cleaned_comment TEXT,
            likes INTEGER,
            published_at TIMESTAMP
        );
        """
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
                conn.commit()

    @task
    def get_comments(video_id):
        API_KEY = os.getenv('YOUTUBE_API_KEY')  # Load API key from environment variable
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
            comments.append({
                'Author': comment['authorDisplayName'],
                'Comment': comment['textDisplay'],
                'Likes': comment['likeCount'],
                'Published At': comment['publishedAt']
            })
        return pd.DataFrame(comments)

    @task
    def preprocess_comments(comments_df):
        stop_words = set(stopwords.words('english'))

        def clean_text(text):
            text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
            text = emoji.replace_emoji(text, replace='')  # Remove emojis
            text = ' '.join([word for word in text.split() if word.lower() not in stop_words])  # Remove stop words
            return text

        comments_df['Cleaned_Comment'] = comments_df['Comment'].apply(clean_text)
        return comments_df

    @task
    def load_to_postgres(preprocessed_df):
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        insert_query = """
        INSERT INTO youtube_comments (author, comment, cleaned_comment, likes, published_at)
        VALUES (%s, %s, %s, %s, %s);
        """
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                for _, row in preprocessed_df.iterrows():
                    cursor.execute(insert_query, (
                        row['Author'],
                        row['Comment'],
                        row['Cleaned_Comment'],
                        row['Likes'],
                        row['Published At']
                    ))
                conn.commit()

    # ✅ Ensure these are indented within the DAG context
    video_id = 'jxCrE2KH7Nk'  # Replace with an actual YouTube video ID
    create_table_task = create_table()
    comments_task = get_comments(video_id)
    preprocessed_comments_task = preprocess_comments(comments_task)
    load_data_task = load_to_postgres(preprocessed_comments_task)

    # ✅ Task dependencies
    create_table_task >> comments_task >> preprocessed_comments_task >> load_data_task