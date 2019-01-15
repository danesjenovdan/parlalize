from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlaposlanci.models import Person
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL

import requests
import json

def getSpeakerMegastring(speaker):

    megastring = u''
    speeches = Speech.getValidSpeeches(datetime.now()).filter(person=speaker)
    for speech in speeches:
        megastring = megastring + ' ' + speech.content

    return megastring

class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

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

        for speaker_id in speaker_ids:
            self.stdout.write('About to begin with speaker %s' % str(speaker_id))
            speaker = Person.objects.filter(id_parladata=speaker_id)
            if not speaker:
                self.stdout.write('Speaker with id %s does not exist' % str(speaker_id))
                return
            else:
                speaker = speaker[0]

            output = [{
                'id': 'p' + str(speaker.id_parladata),
                'content_t': getSpeakerMegastring(speaker),
                'sklic_t': 'VIII',
                'tip_t': 'pmegastring'
            }]

            output = json.dumps(output)

            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})
            self.stdout.write(str(r.content))

        return 0