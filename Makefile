install:
	poetry install
dev:
	poetry run flask --debug --app page_analyzer:app run --port 8000 --host localhost
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
lint:
	poetry run flake8 page_analyzer
schema-load:
	psql page_analyzer < database.sql
db-drop:
	dropdb page_analyzer
	createdb page_analyzer
db-rebuild: db-drop schema-load
build:
	./build.sh
