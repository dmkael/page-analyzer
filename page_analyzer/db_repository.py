from psycopg2.extras import NamedTupleCursor
from datetime import datetime
import psycopg2


class UrlRepo:
    def __init__(self, db_url):
        self.database = db_url

    def connect(self):
        try:
            connection = psycopg2.connect(self.database)
            return connection
        except Exception:
            raise Exception('Unable connect to DB')

    def get_urls_data(self):
        conn = self.connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('''
                SELECT
                    urls.id AS id,
                    urls.name AS name,
                    url_checks.status_code AS status_code,
                    url_checks.created_at AS last_check
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                WHERE url_checks.created_at IN (
                    SELECT MAX(created_at)
                    FROM url_checks
                    GROUP BY url_id
                    ) OR url_checks.created_at IS NULL
                ORDER BY urls.created_at DESC''')
            all_urls_data = cursor.fetchall()
            return all_urls_data

    def get_url_by_id(self, url_id):
        conn = self.connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE id=%s', (url_id,))
            located_url = cursor.fetchone()
            return located_url

    def get_url_checks(self, url_id):
        conn = self.connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('''
                SELECT
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC''', (url_id,))
            url_checks = cursor.fetchall()
            return url_checks

    def get_url_by_name(self, url):
        conn = self.connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name=%s', (url,))
            located_url = cursor.fetchone()
            return located_url

    def save_url(self, url):
        conn = self.connect()
        with conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO urls (name, created_at)
                VALUES (%s, %s)''',
                (url, datetime.utcnow())
            )
            conn.commit()

    def save_url_check(self, url_id, tags_data, status_code):
        conn = self.connect()
        with conn.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO url_checks (
                    url_id,
                    h1,
                    title,
                    description,
                    status_code,
                    created_at)
                VALUES (%s, %s, %s, %s, %s, %s)''',
                (
                    url_id,
                    tags_data['h1'],
                    tags_data['title'],
                    tags_data['description'],
                    status_code,
                    datetime.utcnow()
                )
            )
            conn.commit()
