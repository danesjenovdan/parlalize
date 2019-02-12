from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json


def getSessionMegastring(session):
    speeches = Speech.getValidSpeeches(datetime.now()).filter(session=session)
    megastring = u' '.join([speech.content for speech in speeches])
    return megastring


class Command(BaseCommand):
    help = 'Upload sessions to Solr'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session_ids',
            nargs='+',
            help='Session parladata_id',
            type=int,
        )

    def commit_to_solr(self, output):
        url = SOLR_URL + '/update?commit=true'
        self.stdout.write('About to commit %s sessions to %s' % (str(len(output)), url))
        data = json.dumps(output)
        requests.post(url,
                      data=data,
                      headers={'Content-Type': 'application/json'})

    def handle(self, *args, **options):
        ses_ids = []
        if options['session_ids']:
            ses_ids = options['session_ids']
        else:
            ses_ids = Session.objects.all().values_list('id_parladata', flat=True)

        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        for session_id in ses_ids:
            self.stdout.write('About to begin with session %s' % str(session_id))
            session = Session.objects.filter(id_parladata=session_id)
            if not session:
                self.stdout.write('Session with id %s does not exist' % str(session_id))
                continue
            else:
                session = session[0]

            output = [{
                'term': 'VIII',
                'type': 'session',
                'id': 'session_' + str(session.id_parladata),
                'session_id': session.id_parladata,
                'session_json': json.dumps(static_data['sessions'][str(session.id_parladata)]),
                'org_id': session.organization.id_parladata,
                'start_time': session.start_time.isoformat(),
                'content': getSessionMegastring(session),
                'title': session.name,
            }]

            self.commit_to_solr(output)

        return 0
