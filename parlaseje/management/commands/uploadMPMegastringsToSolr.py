from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlaposlanci.models import Person
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL

import requests
import json


def getSpeakerMegastring(speaker):
    speeches = Speech.getValidSpeeches(datetime.now()).filter(person=speaker)
    megastring = u' '.join([speech.content for speech in speeches])
    return megastring


def commit_to_solr(command, output):
    url = SOLR_URL + '/update?commit=true'
    command.stdout.write('About to commit %s person megastrings to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
                  data=data,
                  headers={'Content-Type': 'application/json'})


class Command(BaseCommand):
    help = 'Upload person megastring to Solr'

    def add_arguments(self, parser):
        parser.add_argument(
            '--speaker_ids',
            nargs='+',
            help='Speaker parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        speaker_ids = []
        if options['speaker_ids']:
            speaker_ids = options['speaker_ids']
        else:
            self.stdout.write('Trying hard with %s/getMPs/' % API_URL)
            members = tryHard(API_URL + '/getMPs/').json()
            speaker_ids = [member['id'] for member in members]

        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        for speaker_id in speaker_ids:
            self.stdout.write('About to begin with speaker %s' % str(speaker_id))
            speaker = Person.objects.filter(id_parladata=speaker_id)
            if not speaker:
                self.stdout.write('Speaker with id %s does not exist' % str(speaker_id))
                continue
            else:
                speaker = speaker[0]

            output = [{
                'term': 'VIII',
                'type': 'pmegastring',
                'id': 'pms_' + str(speaker.id_parladata),
                'person_id': speaker.id_parladata,
                'person_json': json.dumps(static_data['persons'][str(speaker.id_parladata)]),
                'content': getSpeakerMegastring(speaker),
            }]

            commit_to_solr(self, output)

        return 0
