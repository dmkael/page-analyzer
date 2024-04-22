from psycopg2.extras import NamedTupleCursor
from datetime import datetime, timezone
from functools import wraps
import psycopg2


def cursor_decorator(func):
    @wraps(func)
    def wrapper(repo, *args):
        conn = repo.connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            result = func(repo, cursor, *args)
            conn.commit()
            return result
    return wrapper


class UrlRepo:
    def __init__(self, db_url):
        self.database = db_url

    def connect(self):
        connection = psycopg2.connect(self.database)
        return connection

    @cursor_decorator
    def get_urls_data(self, cursor):
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

    @cursor_decorator
    def get_url_by_id(self, cursor, url_id):
        cursor.execute('SELECT * FROM urls WHERE id=%s', (url_id,))
        located_url = cursor.fetchone()
        return located_url

    @cursor_decorator
    def get_url_checks(self, cursor, url_id):
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

    @cursor_decorator
    def get_url_by_name(self, cursor, url):
        cursor.execute('SELECT * FROM urls WHERE name=%s', (url,))
        located_url = cursor.fetchone()
        return located_url

    @cursor_decorator
    def save_url(self, cursor, url):
        cursor.execute(
            '''INSERT INTO urls (name, created_at)
            VALUES (%s, %s)
            RETURNING id''',
            (url, datetime.now(timezone.utc))
        )
        saved_url = cursor.fetchone()
        return saved_url.id

    @cursor_decorator
    def save_url_check(self, cursor, url_id, tags_data, status_code):
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
                datetime.now(timezone.utc)
            )
        )
