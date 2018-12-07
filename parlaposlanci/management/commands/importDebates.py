
from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Debate, AgendaItem
from parlalize.settings import API_URL, PARSER_UN, PARSER_PASS

import requests

def getDataFromPagerApiDRF(url):
    # print(url)
    data = []
    end = False
    page = 1
    url = url+'?limit=300'
    while url:
        response = requests.get(url, auth=requests.auth.HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
        data += response['results']
        url = response['next']
    return data

class Command(BaseCommand):
    help = 'Sets session data'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getSessions/' % API_URL)
        existingISs = list(Debate.objects.all().values_list('id_parladata',
                                                        flat=True))
        data = getDataFromPagerApiDRF(API_URL + '/debates/')
        for item in data:
            if int(item['id']) in existingISs:
                # update
                self.stdout.write('Updating debate %s' % str(item['id']))
                debate = Debate.objects.get(id_parladata=item['id'])
                agenda_items = list(AgendaItem.objects.filter(id_parladata__in=item['agenda_item']))
                debate.agenda_item.add(*agenda_items)
            else:
                # add
                self.stdout.write('Adding debate %s' % str(item['id']))
                debate = Debate(
                    date=item['date'].split('T')[0],
                    id_parladata=item['id'],
                )
                debate.save()
                agenda_items = list(AgendaItem.objects.filter(id_parladata__in=item['agenda_item']))
                debate.agenda_item.add(*agenda_items)
