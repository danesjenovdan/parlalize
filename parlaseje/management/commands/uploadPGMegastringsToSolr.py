from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlaposlanci.models import Person
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL, API_DATE_FORMAT

import requests
import json

def getPGMegastring(org):

    megastring = u''
    speeches = Speech.getValidSpeeches(datetime.now()).filter(person__organisation__id_parladata=org.id_parladata)
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
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

        self.stdout.write('Trying hard with %s/getMembersOfPGsRanges/' % API_URL)
        url = API_URL + '/getMembersOfPGsRanges/' + date_
        membersOfPGsRanges = tryHard(url).json()
        pg_ids = [key for key, value in membersOfPGsRanges[-1]['members'].items()]
        
        for pg_id in pg_ids:
            self.stdout.write('About to begin with PG %s' % str(pg_id))
            pg = Organization.objects.filter(id_parladata=pg_id)
            if not pg:
                self.stdout.write('Organization with id %s does not exist' % str(pg_id))
                return
            else:
                pg = pg[0]
            
            output = [{
                'id': 'pg' + str(pg.id_parladata),
                'content_t': getPGMegastring(pg),
                'sklic_t': 'VIII',
                'tip_t': 'pgmegastring'
            }]

            output = json.dumps(output)

            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})
            self.stdout.write(str(r.content))
        return 0
