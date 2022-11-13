run:
	python manage.py runserver 0.0.0.0:8890

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

shell:
	python manage.py shell

mqtt_sub:
	python manage.py mqtt_sub

target: mqtt_sub run

pipe:
	make install
	make migrate
	make -j2 target
