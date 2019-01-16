from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Legislation
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
        data += response['results']
        url = response['next']
    return data

class Command(BaseCommand):
    help = 'Sets session data'

    def handle(self, *args, **options):
        self.stdout.write('Updating legislation')
    
        self.stdout.write('Getting data from %s/law/' % API_URL)
        laws = getDataFromPagerApiDRF(API_URL + '/law/')
        epas = list(set([law['epa'] for law in laws if law['epa']]))
        hr_acts = [law for law in laws if not law['epa']]
        self.stdout.write('Iterating through EPAs')
        for epa in set(epas):
            self.stdout.write(str(epa))
            laws = requests.get(API_URL + '/law?epa=' + str(epa),
                auth=requests.auth.HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
            # self.stdout.write(laws)
            if int(laws['count']) > 1:
                sorted_date = sorted(laws['results'], key=lambda x: datetime.strptime(x['date'].split('T')[0], '%Y-%m-%d'))
                # self.stdout.write(str(sorted_date))
                sessions = list(set(list([Session.objects.get(id_parladata=int(l['session']))
                            for l 
                            in sorted_date
                            if l['session']])))
                sorted_date = sorted_date[0]
                self.stdout.write('Setting legislation %s' % str(sorted_date['epa']))
                result = Legislation(text=sorted_date['text'],
                                    epa=sorted_date['epa'],
                                    mdt=sorted_date['mdt'],
                                    proposer_text=sorted_date['proposer_text'] if sorted_date['proposer_text'] else None,
                                    procedure_phase=sorted_date['procedure_phase'],
                                    procedure=sorted_date['procedure'],
                                    type_of_law=sorted_date['type_of_law'],
                                    classification=sorted_date['classification'],
                                    date=sorted_date['date'],
                                    status=sorted_date['status'],
                                    #mdt_fk=sorted_date['mdt_fk']
                                    )
                if sorted_date['result']:
                    result.result = sorted_date['result']
                result.save()
                print(sessions)
                if sessions:
                    result.sessions.add(*sessions)
            else:
                self.stdout.write('Setting legislation %s' % str(laws['results'][0]['epa']))
                result = Legislation(text=laws['results'][0]['text'],
                                    epa=laws['results'][0]['epa'],
                                    mdt=laws['results'][0]['mdt'],
                                    proposer_text=laws['results'][0]['proposer_text'],
                                    procedure_phase=laws['results'][0]['procedure_phase'],
                                    procedure=laws['results'][0]['procedure'],
                                    type_of_law=laws['results'][0]['type_of_law'],
                                    classification=laws['results'][0]['classification'],
                                    status=laws['results'][0]['status'],
                                    date=sorted_date['date'],
                                    #mdt_fk=laws['results']['mdt_fk']
                                    )
                result.save()

                if law['session']:
                    # self.stdout.write((law['session']))
                    result.sessions.add(Session.objects.get(id_parladata=int(law['session'])))
                if laws['results'][0]['result']:
                    result.result = laws['results'][0]['result']
                result.save()
        for act in hr_acts:
            result = Legislation(text=act['text'],
                                epa='akt-'+act['uid'],
                                mdt=act['mdt'][:255]  if sorted_date['mdt'] else None,
                                proposer_text=act['proposer_text'][:255]  if sorted_date['proposer_text'] else None,
                                procedure_phase=act['procedure_phase'],
                                procedure=act['procedure'],
                                type_of_law=act['type_of_law'],
                                classification='akt',
                                status=act['status'],
                                #mdt_fk=act['results']['mdt_fk']
                                )
            result.save()
            if act['session']:
                result.sessions.add(Session.objects.get(id_parladata=int(law['session'])))
            if act['result']:
                result.result = act['result']
            result.save()
