
FROM python:3.6.8
ADD ./celery_app/ /app/
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock
WORKDIR /app/
RUN pip install pipenv
RUN pipenv install --system --deploy
USER daemon
ENTRYPOINT celery -A celery_app worker --concurrency=20 --loglevel=info