from __future__ import absolute_import
import os
from datetime import timedelta
from celery.schedules import crontab
from redisbeat.scheduler import RedisScheduler

import logging
logging.basicConfig()
log = logging.getLogger(__name__)

SCRAPE = os.getenv('BEAT_SANTAMONICA_SCRAPE', '*/10')
PDF = os.getenv('BEAT_SANTAMONICA_PDF', '*/20')
log.error("SCRAPE {} PDF {}".format(SCRAPE, PDF))
def santamonica_scheduler(app):
    scheduler = RedisScheduler(app=app)

    scheduler.add(**{'name': 'scrape',
                    'task': 'santamonica.tasks.scrape_councils',
                    'schedule': crontab(minute=SCRAPE), 
                    'args': ()
                    })

    scheduler.add(**{'name': 'pdf',
                    'task': 'santamonica.tasks.process_agenda_to_pdf',
                    'schedule': crontab(minute=PDF), 
                    'args': ()
                    })

    return scheduler