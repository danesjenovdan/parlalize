from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Speech
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json

class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def handle(self, *args, **options):
        # get all valid speeches
        speeches = Speech.getValidSpeeches(datetime.now())

        # get all ids from solr
        self.stdout.write('Getting all IDs from %s/select?wt=json&q=id:*&fl=id&rows=100000000' % SOLR_URL)
        a = requests.get(SOLR_URL + '/select?wt=json&q=id:*&fl=id&rows=100000000')
        indexes = a.json()['response']['docs']

        # find ids of speeches and remove g from begining of id string
        idsInSolr = [int(line["id"].replace('g', ''))
                    for line
                    in indexes if "g" in line["id"]]

        i = 0

        self.stdout.write('Getting all staic data')
        static_data = json.loads(getAllStaticData(None).content)
        for speech in speeches.exclude(id__in=idsInSolr):
            output = [{
                'id': 'g' + str(speech.id_parladata),
                'speaker_i': speech.person.first().id_parladata,
                'session_i': speech.session.id_parladata,
                'org_i': speech.session.organization.id,
                'party_i': speech.organization.id_parladata,
                'datetime_dt': speech.start_time.isoformat(),
                'content_t': speech.content,
                'tip_t': 'govor',
                'the_order': speech.the_order,
                'person': static_data['persons'][str(speech.person.id_parladata)]
            }]

            output = json.dumps(output)

            if i % 100 == 0:
                url = SOLR_URL + '/update?commit=true'
                self.stdout.write('About to commit another 100 speeches to %s/update?commit=true' % SOLR_URL)
                requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})


            else:
                requests.post(SOLR_URL + '/update',
                                  data=output,
                                  headers={'Content-Type': 'application/json'})

            i += 1

        return 0