from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Record
from parlalize.settings import API_URL, PARSER_UN, PARSER_PASS
from datetime import datetime

import requests

def getDataFromPagerApiDRF(url):
    # print(url)
    data = []
    end = False
    page = 1
    url = url+'?limit=300'
    while url:
        response = requests.get(url, auth=requests.auth.HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
        url = response['next']
        yield response['results']

class Command(BaseCommand):
    help = 'Sets records data'

    def handle(self, *args, **options):
        self.stdout.write('Updating records')
        self.stdout.write('Getting data from %s/records/' % API_URL)
        for records in getDataFromPagerApiDRF(API_URL + '/records/'):
            self.stdout.write("Got records")
            for record in records:
                ex_record = Record.objects.filter(id_parladata=record['id'])
                if ex_record:
                    try:
                        ex_record = ex_record[0]
                        ex_record.content=record['content'],
                        ex_record.session=Session.objects.get(id_parladata=record['session']),
                        ex_record.agenda_item=AgendaItem.objects.get(id_parladata=record['agenda_item']),
                        ex_record.gov_id=record['gov_id'],
                        ex_record.save()
                        self.stdout.write('update record')
                    except Exception as e:
                        self.stdout.write(str(e))
                else:
                    try:
                        Record(
                            content=record['content'],
                            session=Session.objects.get(id_parladata=record['session']),
                            agenda_item=AgendaItem.objects.get(id_parladata=record['agenda_item']),
                            gov_id=record['gov_id'],
                            id_parladata=record['id']
                        ).save()
                        self.stdout.write('add record')
                    except Exception as e:
                        self.stdout.write(str(e))
