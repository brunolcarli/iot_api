run:
	python manage.py runserver 0.0.0.0:8890

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

pipe:
	make install
	make migrate
	make run
