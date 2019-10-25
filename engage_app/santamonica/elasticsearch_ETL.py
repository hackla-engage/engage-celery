import engage_scraper
import requests
import json
import time
from datetime import datetime
import socket
import os
import logging

from engage_scraper.scraper_utils import dbutils
from engage_scraper.scraper_logics.santamonica_scraper_models import (AgendaItem, Agenda, 
                                                                    Committee, AgendaRecommendation)
from sqlalchemy import func, desc

engine = dbutils.create_postgres_connection()
Session = dbutils.create_postgres_session(engine)

session = Session()
dev = os.environ.get('ENGAGE_DEBUG')


def getDocumentCount(index_name):
    """
    Get the number of agenda items contained in a specific index. Used to initialize the
    elasticsearch index on set up.

        Args:
            index_name: str, the name of the elastic search index 
        Return:
            document_count: int, the number of agenda items in the index
    """
    url = f'http://es01:9200/{index_name}/_count'
    r = requests.get(url)

    document_count = json.loads(r.text).get('count')

    return document_count


def agendaQuery(init=False, index_name=None):
    """
    This is the main query to get agenda items from the psql database.
        
        Args:
            init: bool, True if this is the initial run (do not check for lastest timestamp)
        Return:

    """
    start = time.time()
    for committee in session.query(Committee):
        committee_id = committee.id 
        committee_name = committee.name
        
        if not init:
            psql_timestamp = getPsqlAidlatestTimestamp(committee_id)
            es_timestamp = getEsLatestTimestamp(index_name)

            if psql_timestamp == es_timestamp:
                print("All items already in Elasticsearch")
                return True

            items = session.query(AgendaItem, AgendaRecommendation)\
                                  .filter(AgendaItem.id==AgendaRecommendation.id)\
                                  .filter(AgendaItem.meeting_time==psql_timestamp)

        else:
            items = session.query(AgendaItem, AgendaRecommendation)\
                                    .filter(AgendaItem.id==AgendaRecommendation.id)
        
        for item in items:
            data = {
                    "date": item[0].meeting_time,
                    "agenda_item_id": item[0].agenda_item_id,
                    "agenda_id": item[0].agenda_id,
                    "title": item[0].title,
                    "recommendations": item[1].recommendation,
                    "body": item[0].body,
                    "department": item[0].department,
                    "sponsors": 'NULL',
                    "tags": 'NULL',
                    "committee": committee_name,
                    "committee_id": committee_id               
            }

            print(f"loading agenda item id {item[0].agenda_item_id} to elasticsearch")
            requests.post(f"http://es01:9200/{index_name}/_doc/?pretty",
                                json=data)

        return f"{items.count()} items loaded from PSQL to Elasticsearch in {int(time.time() - start)} seconds"
        


def getPsqlAidlatestTimestamp(committee_id):
    """
    Returns the most recent timestamp from the psql database for a specified committee
        
        Args:
            committed_id: int, the id of the commitee to be queried
        Return:
            max_timestamp: int, the most recent timestamp from the psql database
    """
    max_timestamp = session.query(func.max(Agenda.meeting_time))\
                                .filter(Agenda.committee_id==committee_id)
    max_timestamp = max_timestamp[0][0]
    
    return max_timestamp


def getEsLatestTimestamp(index_name):
    """
    Returns the most recent timestamp from the elasticsearch database for a specified committee
        
        Args:
            committed_id: int, the id of the commitee to be queried
        Return:
            max_timestamp: int, the most recent timestamp from the psql database
    """
    payload = {
                    "size": 0,
                    "aggs": {
                        "max_date": {               
                        "max": {
                            "field": "date"
                            }
                        }
                    }
                }

    url = f'http://es01:9200/{index_name}/_search?pretty'

    r = requests.post(url, json=payload)
    response = json.loads(r.text)
    timestamp = response.get('aggregations').get('max_date').get('value')

    return int(timestamp)


def loadElasticsearchData():
    document_count = getDocumentCount('agenda_items')
    if document_count == 0:
        return agendaQuery(init=True, index_name='agenda_items')
    else:
        return agendaQuery(index_name='agenda_items')