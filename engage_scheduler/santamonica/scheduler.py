import schedule
import time
import logging
import threading
from os import getenv
from datetime import datetime
import pytz
from . import tasks
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
SANTA_MONICA_PDFS = getenv('SANTA_MONICA_PDFS', "12:05:00").split(":")
SANTA_MONICA_SCRAPE = int(getenv('SANTA_MONICA_SCRAPE', "5"))
SMPDF_HH = int(SANTA_MONICA_PDFS[0])
SMPDF_MM = SANTA_MONICA_PDFS[1]
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def run():
    dt = datetime.now()
    d = datetime(year=dt.year,month=dt.month,day=dt.day,hour=SMPDF_HH, minute=int(SMPDF_MM), tzinfo=pytz.timezone("America/Los_Angeles"))
    utc_timetuple = d.utctimetuple()
    utc_hour = utc_timetuple.tm_hour
    log.info(f"In Santa Monica scheduler, running scraper every {SANTA_MONICA_SCRAPE} minutes")
    log.info(f"Santa Monica Scheduler run PDF generation at: {utc_hour}:{SMPDF_MM} daily")
    schedule.every(SANTA_MONICA_SCRAPE).minutes.do(run_threaded,tasks.scrape_councils)
    schedule.every().day.at(f"{utc_hour}:{SMPDF_MM}").do(run_threaded, tasks.process_agenda_to_pdf)
    while 1:
        schedule.run_pending()
        time.sleep(1)