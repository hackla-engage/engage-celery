from __future__ import absolute_import
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.error("HERE XXXX")
import os
from celery import Celery
from santamonica.scheduler import santamonica_scheduler
from tests.scheduler import tests_scheduler

RABBITMQ_URI = os.getenv('RABBITMQ_URI')
REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
SCHEDULER = os.getenv("SCHEDULER")
TASKS = os.getenv("TASKS")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
log.error('redis://:{}@{}:{}'.format(REDIS_PASSWORD, REDIS_HOSTNAME, REDIS_PORT))
app = Celery('engage_app',
             broker='amqp://{}'.format(RABBITMQ_URI),
             backend='redis://:{}@{}:{}'.format(REDIS_PASSWORD, REDIS_HOSTNAME, REDIS_PORT),
             include=[TASKS])
# not sure if include does everything in file or just looks for tasks
# But replace the santa monica tasks with your tasks!

app.conf.update(
    CELERYBEAT_SCHEDULE={
    },
    CELERY_BEAT_SCHEDULER='redisbeat.RedisScheduler',
    CELERY_REDIS_SCHEDULER_URL='redis://:{}@{}:{}/1'.format(REDIS_PASSWORD, REDIS_HOSTNAME, REDIS_PORT),
    CELERY_REDIS_SCHEDULER_KEY='celery:beat:order_tasks',
)
app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': 'redis://:{}@{}:{}/0'.format(REDIS_PASSWORD, REDIS_HOSTNAME, REDIS_PORT),
        'default_timeout': 20 * 60
    }
}


schedulers = {
    "santamonica": santamonica_scheduler,
    "tests": tests_scheduler
}

scheduler = schedulers[SCHEDULER](app)
