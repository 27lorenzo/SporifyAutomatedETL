import sys
import os
from pathlib import Path

current_script_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_script_path))
file_path = Path(current_script_path).resolve()

# Dynamically add scripts folder to the list of paths to look for imports in
root_repo = file_path.parents[1]
sys.path.insert(1, os.path.join(root_repo, 'scripts'))

import extract_liked_songs
import recommend_songs
import create_playlist

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

dag_args = {
    'owner': 'Spotify ETL',
    'start_date': datetime(2024, 2, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',
    default_args=dag_args,
    description='Spotify DAG',
    schedule_interval="0 0 * * 3", # Every Wednesday
)

t1 = PythonOperator(
    task_id='extract-user-liked-songs',
    python_callable=extract_liked_songs.main,
    dag=dag,
)

t2 = PythonOperator(
    task_id='obtain-recommended-songs',
    python_callable=recommend_songs.main,
    dag=dag,
)

t3 = PythonOperator(
    task_id='create-new-playlist',
    python_callable=create_playlist.main,
    dag=dag,
)

t1 >> t2 >> t3