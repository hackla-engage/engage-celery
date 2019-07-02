#!/bin/sh
until nc -v -w 5 redis 6379; do sleep 2; done
until nc -v -w 5 rabbitmq 5672; do sleep 2; done
rm /engage_app/celerybeat.pid
celery beat -A engage_app -S redisbeat.RedisScheduler
