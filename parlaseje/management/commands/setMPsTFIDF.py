from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, Tfidf
from parlalize.utils_ import saveOrAbortNew, tryHard, getPersonData
from utils.parladata_api import getVotersIDs
from datetime import datetime
from parlalize.settings import ISCI_URL

import requests


def setTfidfOfMP(commander, mp_id):
    url = '%s/tfidf/person?id=%s' % (ISCI_URL, mp_id)
    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)
    commander.stdout.write('Saving speaker %s' % str(mp_id))

    output = r.json()
    date_of = datetime.now().date()
    person = Person.objects.get(id_parladata=mp_id)
    data = output.get('tfidf', [])
    saveOrAbortNew(Tfidf,
                   person=person,
                   created_for=date_of,
                   is_visible=False,
                   data=data)


class Command(BaseCommand):
    help = 'Generate tf-idf for MPs'

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
            self.stdout.write('getVotersIDs')
            speaker_ids = mps_ids = getVotersIDs()

        for speaker_id in speaker_ids:
            setTfidfOfMP(self, speaker_id)

        return 0
