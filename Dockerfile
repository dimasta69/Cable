FROM python:3.11-slim

WORKDIR /app/
COPY . /app

RUN pip install pipenv
RUN pipenv install --dev

CMD ["sh", "-c", "pipenv run python manage.py migrate && pipenv run python manage.py test && pipenv run python create_superuser.py --noinput && pipenv run python manage.py collectstatic --noinput  && pipenv run gunicorn cabel.wsgi:application --bind 0.0.0.0:8000"]