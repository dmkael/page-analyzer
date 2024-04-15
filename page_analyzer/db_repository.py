from psycopg2.extras import NamedTupleCursor
from datetime import datetime
import psycopg2


class UrlRepo:
    def __init__(self, db_url):
        try:
            self.connection = psycopg2.connect(db_url)
        except Exception:
            raise Exception('Unable connect to DB')

    def get_urls_data(self):
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
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

    def get_url_data(self, url_id):
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE id=%s', (url_id, ))
            url_from_db = cursor.fetchone()
            return url_from_db

    def get_url_checks(self, url_id):
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
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
                ORDER BY created_at DESC''', (url_id, ))
            url_checks = cursor.fetchall()
            return url_checks

    def find_url(self, url):
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name=%s', (url,))
            url_from_db = cursor.fetchone()
            return url_from_db

    def save_url(self, url):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO urls (name, created_at)
                VALUES (%s, %s)''',
                (url, datetime.now()))
            self.connection.commit()

    def create_url_check(self, url_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO url_checks (url_id, created_at)
                VALUES (%s, %s)''',
                (url_id, datetime.now()))
            self.connection.commit()
