#!/bin/sh
docker-compose -f docker-compose-test.yml up --abort-on-container-exit --exit-code-from celery_worker
if [ $? -eq 0 ]; then
    echo Succeeded building and testing
    docker push hack4laengage/engage_celery
    exit 0;
else
    echo Failed building and testing
    exit 1;
fi
