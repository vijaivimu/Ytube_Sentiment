from airflow import DAG
from airflow.decorators import task  # Importing Airflow's task decorator
from datetime import datetime, timedelta

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),  # Set to a past date
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'math_operations_dag_taskflow',
    default_args=default_args,
    description='A DAG that performs a sequence of mathematical operations using @task',
    schedule_interval=None,  # Manual execution
    catchup=False
) as dag:

    # Task 1: Initialize X
    @task
    def start_task():
        X = 10  # Initial value
        print(f"Task 1: Initial value of X = {X}")
        return X  # Return X to pass it to the next task

    # Task 2: Add 5 to X
    @task
    def add_five(X: int):
        X += 5
        print(f"Task 2: After adding 5, X = {X}")
        return X

    # Task 3: Multiply X by 2
    @task
    def multiply_by_two(X: int):
        X *= 2
        print(f"Task 3: After multiplying by 2, X = {X}")
        return X

    # Task 4: Subtract 4 from X
    @task
    def subtract_four(X: int):
        X -= 4
        print(f"Task 4: After subtracting 4, X = {X}")
        return X

    # Task 5: Square X
    @task
    def square_X(X: int):
        X = X ** 2
        print(f"Task 5: After squaring, X = {X}")
        return X

    # Define Task Dependencies
    X_initial = start_task()
    X_added = add_five(X_initial)
    X_multiplied = multiply_by_two(X_added)
    X_subtracted = subtract_four(X_multiplied)
    X_final = square_X(X_subtracted)