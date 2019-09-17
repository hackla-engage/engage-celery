
FROM python:3.7-alpine
# A side effect of using alpine is you must build psycopg2 from source
RUN apk update && apk add postgresql-dev gcc musl-dev netcat-openbsd jpeg-dev zlib-dev texlive texmf-dist-bibtexextra texmf-dist-latexextra texmf-dist-formatsextra
ENV LIBRARY_PATH=/lib:/usr/lib

ADD . /engage_app/
WORKDIR /engage_app/
RUN mkdir /pdfs
RUN pip install --upgrade pip
RUN pip install -U -r requirements.txt
RUN adduser -D -u 1000 celery
RUN chown -R celery:celery /engage_app 
RUN chown -R celery:celery /pdfs
USER celery