import os
from datetime import datetime
import requests
from airflow import DAG
from airflow.decorators import task
import logging

from airflow.operators.python import PythonOperator

import logging
import os
import shutil
import sys
import json
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup

import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '')) + '//'
EXTRACT_PATH = '/opt/airflow/dags/input/'
LOAD_PATH = '/opt/airflow/dags/output/'

with DAG(
    dag_id='daily_data_processing_pipeline',
    description='data processing pipeline',
    schedule_interval='0 1 * * *',
    start_date=datetime(2022, 9, 30), catchup=False) as dag:

    @task
    def start_task():
        logging.info('Task Triggered')
        logging.info(datetime.utcnow().isoformat())

    @task
    def extract(filename):
        filepath = f"{EXTRACT_PATH}{filename}"
        logging.info('Input File Path')
        logging.info(filepath)

        df = pd.read_csv(filepath)
        df = df.to_json(orient="records")
        df = json.loads(df)
        return df

    @task
    def transform(df):
        df = pd.json_normalize(df)

        # Delete any rows which do not have a `name` (null or "")
        df['name'].replace('', np.nan, inplace=True)
        df.dropna(subset=['name'], inplace=True)

        # Split the `name` field into `first_name`, and `last_name`
        prefix_to_remove = ['Dr.','Miss','Mr.','Mrs.','Ms.'] # note: suffix doesnt really matter since we take the first two elements after the prefix (if it exists)
        def get_first_last_name(full_name):
            first_name = None
            last_name = None
            name_split = full_name.split(" ")
            for name in name_split:
                if name not in prefix_to_remove:
                    if not first_name:
                        first_name = name
                    elif not last_name:
                        last_name = name
            if not first_name:
                first_name = ''
            if not last_name:
                last_name = ''

            return [first_name, last_name]
        df['first_name'],df['last_name'] = zip(*df['name'].apply(lambda x: get_first_last_name(x)))

        # Delete any rows which do not have both `first_name` and `last_name` ("")
        df['first_name'].replace('', np.nan, inplace=True)
        df['last_name'].replace('', np.nan, inplace=True)
        df.dropna(subset=['first_name','last_name'], inplace=True)
        
        # remove leading zeros by converting price to float
        df['price'] = df['price'].astype(float)

        # Create a new field named `above_100`, which is `true` if the price is strictly greater than 100
        df['above_100'] = df['price']>100

        # rearrange columns and remove `name``
        df = df[['first_name','last_name','price','above_100']]

        df = df.to_json(orient="records")
        df = json.loads(df)

        return df

    @task
    def load(filename, df):
        df = pd.json_normalize(df)

        if not os.path.exists(LOAD_PATH):
            os.mkdir(LOAD_PATH)
        filepath = f"{LOAD_PATH}{filename}"
        logging.info('Output File Path')
        logging.info(filepath)

        df.to_csv(filepath, index=False)

    with TaskGroup('dataset1') as dataset1:
        data = extract('dataset1.csv')
        transformed_data = transform(data)
        load('dataset1.csv', transformed_data)
    
    with TaskGroup('dataset2') as dataset2:
        data = extract('dataset2.csv')
        transformed_data = transform(data)
        load('dataset2.csv', transformed_data)

    start_task() >> [dataset1, dataset2]