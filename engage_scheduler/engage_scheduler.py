from sys import argv, exit
import importlib
from os import getenv
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
if __name__ == "__main__":
    log.error("starting scheduler")
    scheduler_module = getenv('ENGAGE_SCHEDULER')
    scheduler = importlib.import_module(scheduler_module)
    scheduler.run()
    
