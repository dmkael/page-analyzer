from flask import Flask, render_template, request, redirect, url_for
from flask import flash, get_flashed_messages
from validators.url import url as url_validator
from urllib.parse import urlparse, urlunparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from page_analyzer.db_repository import UrlRepo
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo = UrlRepo(DATABASE_URL)


def validate_url(url):
    try:
        parsed_url = urlparse(url)
        if all([parsed_url.scheme, parsed_url.netloc]) and len(url) > 255:
            return 'URL превышает 255 символов', 'error'
    except ValueError:
        return 'Некорректный URL', 'error'
    if url_validator(url) is not True:
        return 'Некорректный URL', 'error'


def get_timezone_delta():
    return datetime.now() - datetime.utcnow()


@app.route('/')
def main():
    return render_template(
        'index.html',
        messages=()
    ), 200


@app.post('/urls')
def post_url():
    data = request.form.to_dict()
    url = data.get('url').lower()

    errors = validate_url(url)
    if errors:
        flash(*errors)
        return render_template(
            'index.html',
            messages=get_flashed_messages(with_categories=True)
        ), 422

    parsed_url = urlparse(url)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    exist_url = repo.get_url_by_name(new_url)

    if exist_url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', url_id=exist_url.id), 302)

    repo.save_url(new_url)
    flash('Страница успешно добавлена', 'success')
    new_url = repo.get_url_by_name(new_url)
    return redirect(url_for('get_url', url_id=new_url.id), 302)


@app.get('/urls')
def get_urls():
    urls = repo.get_urls_data()
    return render_template(
        'urls/index.html',
        urls=urls,
        time_delta=get_timezone_delta()
    ), 200


@app.get('/urls/<int:url_id>')
def get_url(url_id):
    url = repo.get_url_by_id(url_id)
    if not url:
        return render_template(
            'not_found.html'
        ), 404
    return render_template(
        'urls/show.html',
        url=url,
        messages=get_flashed_messages(with_categories=True),
        url_checks=repo.get_url_checks(url_id),
        time_delta=get_timezone_delta()
    ), 200


def extract_tags_data(content):
    soup = BeautifulSoup(content, "html.parser")
    h1 = soup.h1
    title = soup.title
    description = soup.find('meta', attrs={'name': 'description'})
    tags_data = {
        'h1': h1.string if h1 else '',
        'title': title.string if title else '',
        'description': description.get('content', '') if description else ''
    }
    return tags_data


@app.post('/urls/<int:url_id>/checks')
def post_url_check(url_id):
    url = repo.get_url_by_id(url_id)
    try:
        response = requests.get(url.name, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', url_id=url_id), 302)
    tags_data = extract_tags_data(response.content)
    repo.save_url_check(url_id, tags_data, response.status_code)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', url_id=url_id), 302)


@app.errorhandler(404)
def not_found(e):
    return render_template('not_found.html'), 404
