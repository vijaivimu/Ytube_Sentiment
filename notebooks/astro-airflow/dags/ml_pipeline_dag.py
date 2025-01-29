from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),  # Change as needed
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'ml_pipeline_dag',
    default_args=default_args,
    description='A simple ML pipeline DAG with preprocessing, training, and evaluation',
    schedule_interval=None,  # Manual trigger
)

# Define Python functions for tasks
def preprocessing():
    print("Step 1: Preprocessing data...")

def train_model():
    print("Step 2: Training model...")

def evaluate_model():
    print("Step 3: Evaluating model...")

# Define tasks
task_preprocessing = PythonOperator(
    task_id='preprocessing',
    python_callable=preprocessing,
    dag=dag,
)

task_train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

task_evaluate_model = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

# Set task dependencies (execution order)
task_preprocessing >> task_train_model >> task_evaluate_model