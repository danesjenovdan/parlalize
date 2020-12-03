from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from utils.parladata_api import getParentOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json


def getSessionMegastring(session):
    speeches = Speech.getValidSpeeches(datetime.now()).filter(session=session)
    megastring = u' '.join([speech.content for speech in speeches])
    return megastring


def commit_to_solr(commander, output):
    url = SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s sessions to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
                  data=data,
                  headers={'Content-Type': 'application/json'})

def uploadSessionToSolr(commander, ses_ids):
    static_data = json.loads(getAllStaticData(None).content)

    commander.stdout.write('Sessions for upload %s' % str(ses_ids))
    for session_id in ses_ids:
        commander.stdout.write('About to begin with session %s' % str(session_id))
        session = Session.objects.filter(id_parladata=session_id)
        if not session:
            commander.stdout.write('Session with id %s does not exist' % str(session_id))
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

        commit_to_solr(commander, output)


class Command(BaseCommand):
    help = 'Upload sessions to Solr'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session_ids',
            nargs='+',
            help='Session parladata_id',
            type=int,
        )
        parser.add_argument(
            '--fast',
            action='store_true',
            help='Upload just last 2 sessions',
        )

    def handle(self, *args, **options):
        ses_ids = []
        if options['session_ids']:
            ses_ids = options['session_ids']
        else:
            if options['fast']:
                orgs = getParentOrganizationsWithVoters()
                sessions = Session.objects.filter(organization__id_parladata__in=orgs).order_by('-start_time')
                ses_ids = sessions[:2].values_list('id_parladata', flat=True)
            else:
                ses_ids = Session.objects.all().values_list('id_parladata', flat=True)

        # get static data
        self.stdout.write('Getting all static data')

        uploadSessionToSolr(self, ses_ids)

        return 0
