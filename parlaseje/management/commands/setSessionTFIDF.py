from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Session, Tfidf
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import ISCI_URL

import requests


def setTfidfOfSession(commander, session_id):
    url = '%s/tfidf/session?id=%s' % (ISCI_URL, session_id)
    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)
    commander.stdout.write('Saving session %s' % str(session_id))

    output = r.json()
    date_of = datetime.now().date()
    session = Session.objects.get(id_parladata=session_id)
    data = output.get('tfidf', [])
    saveOrAbortNew(Tfidf,
                   session=session,
                   created_for=date_of,
                   is_visible=False,
                   data=data)


class Command(BaseCommand):
    help = 'Generate tf-idf for sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session_ids',
            nargs='+',
            help='Session parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        ses_ids = []
        if options['session_ids']:
            ses_ids = options['session_ids']
        else:
            ses_ids = Session.objects.all().values_list('id_parladata', flat=True)

        for session_id in ses_ids:
          setTfidfOfSession(self, session_id)

        return 0
