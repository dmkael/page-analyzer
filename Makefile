install:
	poetry install
dev:
	poetry run flask --debug --app page_analyzer:app run --port 8000
gunicorn:
	poetry run gunicorn --workers=4 --bind=127.0.0.1:8000 page_analyzer:app
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
lint:
	poetry run flake8 page_analyzer