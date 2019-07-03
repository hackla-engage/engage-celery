from __future__ import absolute_import
from datetime import timedelta
from celery.schedules import crontab
from redisbeat.scheduler import RedisScheduler

import logging
logging.basicConfig()
log = logging.getLogger(__name__)

def santamonica_scheduler(app):
    scheduler = RedisScheduler(app=app)

    scheduler.add(**{'name': 'scrape',
                    'task': 'santamonica.tasks.scrape_councils',
                    'schedule': crontab(minute="*/10"), 
                    'args': ()
                    })

    scheduler.add(**{'name': 'pdf',
                    'task': 'santamonica.tasks.process_agenda_to_pdf',
                    'schedule': crontab(minute="*/20"), 
                    'args': ()
                    })

    return scheduler