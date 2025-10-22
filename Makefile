run:
	python manage.py runserver

app:
	python manage.py startapp apps

mig:
	python manage.py makemigrations
	python manage.py migrate

user:
	python manage.py createsuperuser

reset:
	python manage.py flush