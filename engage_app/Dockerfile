
FROM python:3.7.3-alpine
# A side effect of using alpine is you must build psycopg2 from source
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev netcat-openbsd jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

ADD . /engage_app/
WORKDIR /engage_app/
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN adduser -D -u 1000 celery
RUN chown -R celery:celery /engage_app
USER celery
