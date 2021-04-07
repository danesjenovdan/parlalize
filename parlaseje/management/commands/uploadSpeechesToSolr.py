from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Speech
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json


def commit_to_solr(commander, output):
    url = SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s speeches to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
                  data=data,
                  headers={'Content-Type': 'application/json'})


def deleteUnvalidSpeeches(solr_ids, speeches):
    speeches = list(speeches.values_list('id_parladata', flat=True))

    idsForDelete = list(set(solr_ids) - set(speeches))

    idsForDelete = ['speech_' + str(i) for i in idsForDelete]

    data = {'delete': idsForDelete
            }

    r = requests.post(SOLR_URL + '/update?commit=true',
                        data=json.dumps(data),
                        headers={'Content-Type': 'application/json'})

    print(r.text)
    return True


class Command(BaseCommand):
    help = 'Uploads speeches to Solr'

    def handle(self, *args, **options):
        # get all ids from solr
        url = SOLR_URL + '/select?wt=json&q=type:speech&fl=speech_id&rows=100000000'
        self.stdout.write('Getting all IDs from %s' % url)
        a = requests.get(url)
        docs = a.json()['response']['docs']
        idsInSolr = [doc['speech_id'] for doc in docs if 'speech_id' in doc]

        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        # get all valid speeches
        self.stdout.write('Getting valid speeches')
        speeches = Speech.getValidSpeeches(datetime.now())

        deleteUnvalidSpeeches(idsInSolr, speeches)

        i = 1
        output = []
        for speech in speeches.exclude(id_parladata__in=idsInSolr):
            output.append({
                'term': 'VIII',
                'type': 'speech',
                'id': 'speech_' + str(speech.id_parladata),
                'speech_id': speech.id_parladata,
                'person_id': speech.person.first().id_parladata,
                'person_json': json.dumps(static_data['persons'][str(speech.person.first().id_parladata)]),
                'party_id': speech.organization.id_parladata,
                'session_id': speech.session.id_parladata,
                'session_json': json.dumps(static_data['sessions'][str(speech.session.id_parladata)]),
                'org_id': speech.session.organization.id_parladata,
                'start_time': speech.start_time.isoformat(),
                'the_order': speech.the_order,
                'content': speech.content,
            })

            if i % 100 == 0:
                commit_to_solr(self, output)
                output = []

            i += 1

        if len(output):
            commit_to_solr(self, output)

        return 0
