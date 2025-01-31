from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import math

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),  # Set to a past date
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'math_operations_dag',
    default_args=default_args,
    description='A DAG that performs a sequence of mathematical operations',
    schedule_interval=None,  # Manual execution
)

# Task 1: Initialize X
def start_task(**kwargs):
    X = 10  # Initial value
    print(f"Task 1: Initial value of X = {X}")
    kwargs['ti'].xcom_push(key='X', value=X)  # Store X in XCom


# Task 2: Add 5 to X
def add_five(**kwargs):
    ti = kwargs['ti']
    X = ti.xcom_pull(task_ids='start_task', key='X')
    X += 5
    print(f"Task 2: After adding 5, X = {X}")
    ti.xcom_push(key='X', value=X)

# Task 3: Multiply X by 2
def multiply_by_two(**kwargs):
    ti = kwargs['ti']
    X = ti.xcom_pull(task_ids='add_five', key='X')
    X *= 2
    print(f"Task 3: After multiplying by 2, X = {X}")
    ti.xcom_push(key='X', value=X)

# Task 4: Subtract 4 from X
def subtract_four(**kwargs):
    ti = kwargs['ti']
    X = ti.xcom_pull(task_ids='multiply_by_two', key='X')
    X -= 4
    print(f"Task 4: After subtracting 4, X = {X}")
    ti.xcom_push(key='X', value=X)

# Task 5: Square X
def square_X(**kwargs):
    ti = kwargs['ti']
    X = ti.xcom_pull(task_ids='subtract_four', key='X')
    X = X ** 2
    print(f"Task 5: After squaring, X = {X}")
    ti.xcom_push(key='X', value=X)

# Define Airflow Tasks
task1 = PythonOperator(
    task_id='start_task',
    python_callable=start_task,
    provide_context=True,
    dag=dag,
)

task2 = PythonOperator(
    task_id='add_five',
    python_callable=add_five,
    provide_context=True,
    dag=dag,
)

task3 = PythonOperator(
    task_id='multiply_by_two',
    python_callable=multiply_by_two,
    provide_context=True,
    dag=dag,
)

task4 = PythonOperator(
    task_id='subtract_four',
    python_callable=subtract_four,
    provide_context=True,
    dag=dag,
)

task5 = PythonOperator(
    task_id='square_X',
    python_callable=square_X,
    provide_context=True,
    dag=dag,
)

# Define Task Dependencies
task1 >> task2 >> task3 >> task4 >> task5