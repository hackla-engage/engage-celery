FROM python:3-slim
# A side effect of using alpine is you must build psycopg2 from source
RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc g++ make postgresql-contrib texlive-latex-base texlive-latex-recommended
ENV LIBRARY_PATH=/lib:/usr/lib
ADD . /engage_scheduler
WORKDIR /engage_scheduler
RUN mkdir /pdfs
RUN pip install -U -r requirements.txt
CMD [ "python", "./engage_scheduler.py" ]