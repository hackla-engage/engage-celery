from __future__ import absolute_import
from celery_app.engage_app import app
from engage_scraper.scraper_logics.santamonica_scraper_models import Committee, Agenda
from engage_scraper.scraper_utils import dbutils
from engage_scraper.scraper_logics.santamonica_scraper_logic import SantaMonicaScraper
from celery.schedules import crontab

import logging
logging.basicConfig()
log = logging.getLogger(__name__)

council_names_to_add_to_schedule = dict()
engine = dbutils.create_postgres_connection()
Session = dbutils.create_postgres_session(engine)


@app.task(bind=True, default_retry=10)
def find_council_names_to_add_to_schedule(self):
    session = Session()
    committees = session.query(Committee).all()
    for committee in committees:
        if committee.name not in council_names_to_add_to_schedule.keys():
            council_names_to_add_to_schedule[committee.name] = {

            }


@app.task(bind=True, default_retry=10)
def scrape_councils(self):
    # Make sure you have set the POSTGRES_URI and POSTGRES_DB env variables
    session = Session()
    result = []
    for committee in session.query(Committee):
        scraper = SantaMonicaScraper(committee=committee.name,
                                     tz_string=committee.location_tz,
                                     base_agenda_location=committee.base_agenda_location,
                                     agendas_table_location=committee.agendas_table_location
                                     )
        scraper.get_available_agendas()
        scraper.scrape()
        result.append(committee.name)
