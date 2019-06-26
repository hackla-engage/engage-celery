from __future__ import absolute_import
import os
from celery import Celery
import logging
logging.basicConfig()
log = logging.getLogger(__name__)

RABBITMQ_URI = os.getenv('RABBITMQ_URI')
REDIS_URI = os.getenv("REDIS_URI")
log.error("GOT URI: {}".format(RABBITMQ_URI))
app = Celery('celery_app',
             broker='amqp://{}'.format(RABBITMQ_URI),
             backend='redis://{}'.format(REDIS_URI),
             include=['celery_app.tasks'])
