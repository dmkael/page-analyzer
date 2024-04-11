from flask import Flask, render_template, request, redirect, url_for
from flask import flash, get_flashed_messages
from validators.url import url as url_validator
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse
from datetime import datetime
from psycopg2.extras import NamedTupleCursor
import os
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def connect_to_db(db_url):
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except ConnectionError:
        raise ConnectionError('Connect to DB is failed')


def flash_url_errors(url):
    try:
        parsed_url = urlparse(url)
        if all([parsed_url.scheme, parsed_url.netloc]) and len(url) > 255:
            flash('URL превышает 255 символов', 'error')
            return
    except ValueError:
        flash('Некорректный URL', 'error')
    if url_validator(url) is not True:
        flash('Некорректный URL', 'error')


def get_all_urls_from_db():
    conn = connect_to_db(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls')
        all_urls = cursor.fetchall()
        return all_urls


def get_url_from_db(url_id):
    conn = connect_to_db(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls WHERE id=%s', (url_id,))
        url_from_db = cursor.fetchone()
        return url_from_db


def find_url_in_db(url):
    conn = connect_to_db(DATABASE_URL)
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls WHERE name=%s', (url,))
        url_from_db = cursor.fetchone()
        return url_from_db


def save_url_into_db(url):
    conn = connect_to_db(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute(
            '''INSERT INTO urls (name, created_at)
            VALUES (%s, %s)''',
            (url, datetime.utcnow()))
        conn.commit()


@app.route('/')
def main():
    return render_template(
        'index.html',
        messages=[]
    )


@app.post('/urls')
def post_url():
    data = request.form.to_dict()
    url = data.get('url')
    flash_url_errors(url)
    errors = get_flashed_messages(with_categories=True)
    if errors:
        return render_template(
            'index.html',
            messages=errors
        )
    parsed_url = urlparse(url)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    exist_url = find_url_in_db(new_url)
    if exist_url:
        flash('Cтраница уже существует', 'info')
        url_id = exist_url.id
        return redirect(url_for('get_url', url_id=url_id), 302)
    save_url_into_db(new_url)
    flash('Cтраница успешно добавлена', 'success')
    new_url = find_url_in_db(new_url)
    return redirect(url_for('get_url', url_id=new_url.id), 302)


@app.get('/urls')
def get_urls():
    all_urls = get_all_urls_from_db()
    return render_template(
        'urls/index.html',
        sites=all_urls
    )


@app.get('/urls/<int:url_id>')
def get_url(url_id):
    if not get_url_from_db(url_id):
        return render_template(
            'not_found.html'
        ), 404
    return render_template(
        'urls/show.html',
        site=get_url_from_db(url_id),
        messages=get_flashed_messages(with_categories=True)
    )


@app.errorhandler(404)
def not_found(e):
    return render_template('not_found.html'), 404
