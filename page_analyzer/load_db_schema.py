import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect(db_url):
    try:
        connection = psycopg2.connect(db_url)
        return connection
    except Exception:
        raise Exception('Unable connect to DB')


def load_schema():
    conn = connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                name VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP NOT NULL
            );''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS url_checks (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                url_id BIGINT REFERENCES urls (id) ON DELETE CASCADE NOT NULL,
                status_code INT,
                h1 TEXT,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP NOT NULL
            );''')
        conn.commit()


if __name__ == "__main__":
    load_schema()
