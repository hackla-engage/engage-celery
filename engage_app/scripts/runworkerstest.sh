#!/bin/sh
printenv
until nc -v -w 5 redis 6379; do sleep 2; done
until nc -v -w 5 rabbitmq 5672; do sleep 2; done
rm output.txt
rm *log
celery worker -A engage_app -l info -c1&
sleep 60
pkill -9 -f 'celery worker'
if [ -f output.txt ]; then
    echo Test task ran successfully
    exit 0
else
    echo Test task did not run
    exit 1
fi
