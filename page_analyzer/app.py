from flask import Flask, render_template, request, redirect, url_for
from flask import flash, get_flashed_messages
from validators.url import url as url_validator
from urllib.parse import urlparse, urlunparse
import requests
from dotenv import load_dotenv
from page_analyzer.db_repository import UrlRepo
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo = UrlRepo(DATABASE_URL)


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


@app.route('/')
def main():
    return render_template(
        'index.html',
        messages=[]
    )


@app.post('/urls')
def post_url():
    data = request.form.to_dict()
    url = data.get('url').lower()
    flash_url_errors(url)
    errors = get_flashed_messages(with_categories=True)
    if errors:
        return render_template(
            'index.html',
            messages=errors
        )
    parsed_url = urlparse(url)
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    exist_url = repo.find_url(new_url)
    if exist_url:
        flash('Cтраница уже существует', 'info')
        return redirect(url_for('get_url', url_id=exist_url.id), 302)
    repo.save_url(new_url)
    flash('Cтраница успешно добавлена', 'success')
    new_url = repo.find_url(new_url)
    return redirect(url_for('get_url', url_id=new_url.id), 302)


@app.get('/urls')
def get_urls():
    urls = repo.get_urls_data()
    return render_template(
        'urls/index.html',
        urls=urls
    )


@app.get('/urls/<int:url_id>')
def get_url(url_id):
    url = repo.get_url_data(url_id)
    if not url:
        return render_template(
            'not_found.html'
        ), 404
    return render_template(
        'urls/show.html',
        url=url,
        messages=get_flashed_messages(with_categories=True),
        url_checks=repo.get_url_checks(url_id)
    )


@app.post('/urls/<int:url_id>/checks')
def post_check(url_id):
    url = repo.get_url_data(url_id)
    try:
        data = requests.get(url.name, timeout=5)
    except requests.exceptions.ConnectionError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', url_id=url_id))
    except requests.exceptions.ReadTimeout:
        flash('Превышен интервал ожидания при проверке', 'danger')
        return redirect(url_for('get_url', url_id=url_id))
    if data.status_code > 299 or data.status_code < 200:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', url_id=url_id))
    repo.create_url_check(url_id, data.status_code)
    flash('Cтраница успешно проверена', 'success')
    return redirect(url_for('get_url', url_id=url_id))


@app.errorhandler(404)
def not_found(e):
    return render_template('not_found.html'), 404
