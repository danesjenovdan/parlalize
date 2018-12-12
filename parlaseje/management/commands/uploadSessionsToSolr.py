from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json

def getSessionContent(session):

    megastring = u''
    speeches = Speech.getValidSpeeches(datetime.now()).filter(session=session)
    for speech in speeches:
        megastring = megastring + ' ' + speech.content

    return megastring

class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

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
            self.stdout.write('About to begin with session %s' % str(session_id))
            session = Session.objects.filter(id_parladata=session_id)
            if not session:
                self.stdout.write('Session with id %s does not exist' % str(session_id))
                return
            else:
                session = session[0]

            output = [{
                'id': 's' + str(session.id_parladata),
                'org_i': session.organization.id,
                'datetime_dt': session.start_time.isoformat(),
                'content_t': getSessionContent(session),
                'sklic_t': 'VII',
                'tip_t': 'seja'
            }]

            output = json.dumps(output)

            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})

        return 0