import requests
import pandas as pd
from psycopg2 import connect
from datetime import timedelta

headers = {'Content-Type': 'application/json'}

def get_raw_c19_data(api_get_start_date=None):
    api_url = 'https://api.covid19api.com/total/country/singapore'
    if api_get_start_date:
        api_url += f'?from={api_get_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")}'
    print(api_url)

    api_response = requests.get(api_url, headers=headers)
    if api_response.status_code != 200:
        raise ValueError('Invalid Status Code from API')
    
    return api_response.json()

def get_postgres_db_connection():
    conn = connect(
        dbname = 'postgres',
        user = 'postgres',
        host = 'localhost',
        port = '3010',
        password = 'password'
    )
    
    return conn

def get_api_start_date():
    conn = get_postgres_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(Date) FROM covidCases')
    
    try:
        max_date = cursor.fetchall()[0][0] + timedelta(days=1)
    except:
        max_date = None
    
    cursor.close()
    conn.close()

    return max_date

def get_and_write_c19_data():
    api_get_start_date = get_api_start_date()
    api_response_json = get_raw_c19_data(api_get_start_date)
    df = pd.DataFrame(api_response_json)
    df['Date'] = pd.to_datetime(df['Date'])

    conn = get_postgres_db_connection()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute("INSERT INTO covidCases (Country, Lat, Lon, Confirmed, Deaths, Recovered, Active, Date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (row['Country'], row['Lat'], row['Lon'], row['Confirmed'], row['Deaths'], row['Recovered'], row['Active'], row['Date']))
    conn.commit()

    cursor.close()
    conn.close()

if __name__ == '__main__':
    get_and_write_c19_data()