from __future__ import absolute_import
from datetime import timedelta
from redisbeat.scheduler import RedisScheduler

def tests_scheduler(app):
    scheduler = RedisScheduler(app=app)

    scheduler.add(**{'name': 'test',
                    'task': 'tests.tasks.sendtest',
                    'schedule': timedelta(seconds=20), 
                    'args': ()
                    })


    return scheduler