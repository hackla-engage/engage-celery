from __future__ import absolute_import
import sys
from celery.exceptions import CeleryError, SystemTerminate
from threading import Timer
from engage_app import app
from datetime import datetime
from celery_once import QueueOnce
import logging
logging.basicConfig()
log = logging.getLogger(__name__)

@app.task(bind=True)
def sendtest(self):
    with open('output.txt', 'w') as f:
        f.write("True")

