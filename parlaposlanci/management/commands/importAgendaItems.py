from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import AgendaItem
from parlalize.settings import API_URL, PARSER_UN, PARSER_PASS
from utils.parladata_api import getAgendaItems

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
        self.stdout.write('Fetching data from %s/agenda-items/' % API_URL)
        existingISs = list(AgendaItem.objects.all().values_list('id_parladata',
                                                            flat=True))
        data = getAgendaItems()
        for item in data:
            if int(item['id']) in existingISs:
                pass
            else:
                AgendaItem(
                    session=Session.objects.get(id_parladata=item['session']),
                    title=item['name'],
                    id_parladata=item['id']
                ).save()
