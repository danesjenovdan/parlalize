from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Speech
from parlaposlanci.models import Person
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from utils.parladata_api import getOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL, API_DATE_FORMAT

import requests
import json


def getOrgMegastring(org):
    speeches = Speech.getValidSpeeches(datetime.now()).filter(organization__id_parladata=org.id_parladata)
    megastring = u' '.join([speech.content for speech in speeches])
    return megastring


def commit_to_solr(commander, output):
    url = SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s pg megastrings to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
                  data=data,
                  headers={'Content-Type': 'application/json'})


class Command(BaseCommand):
    help = 'Upload pg megastring to Solr'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pg_ids',
            nargs='+',
            help='PG parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        pg_ids = []
        if options['pg_ids']:
            pg_ids = options['pg_ids']
        else:
            date_of = datetime.now().date()
            date_ = date_of.strftime(API_DATE_FORMAT)

            pg_ids = getOrganizationsWithVoters(date_=date_of)

        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        for pg_id in pg_ids:
            self.stdout.write('About to begin with PG %s' % str(pg_id))
            pg = Organization.objects.filter(id_parladata=pg_id)
            if not pg:
                self.stdout.write('Organization with id %s does not exist' % str(pg_id))
                continue
            else:
                pg = pg[0]

            output = [{
                'term': 'VIII',
                'type': 'pgmegastring',
                'id': 'pgms_' + str(pg.id_parladata),
                'party_id': pg.id_parladata,
                'party_json': json.dumps(static_data['partys'][str(pg.id_parladata)]),
                'content': getOrgMegastring(pg),
            }]

            commit_to_solr(self, output)

        return 0
