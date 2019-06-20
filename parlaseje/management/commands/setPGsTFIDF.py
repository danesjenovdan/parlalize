from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, Tfidf
from parlalize.utils_ import saveOrAbortNew, tryHard
from utils.parladata_api import getOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT, ISCI_URL

import requests


def setTfidfOfPG(commander, pg_id):
    url = '%s/tfidf/party?id=%s' % (ISCI_URL, pg_id)
    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)
    commander.stdout.write('Saving PG %s' % str(pg_id))

    output = r.json()
    date_of = datetime.now().date()
    organization = Organization.objects.get(id_parladata=pg_id)
    data = output.get('tfidf', [])
    saveOrAbortNew(Tfidf,
                   organization=organization,
                   created_for=date_of,
                   is_visible=False,
                   data=data)


class Command(BaseCommand):
    help = 'Generate tf-idf for PGs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization_ids',
            nargs='+',
            help='Organization parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

        organization_ids = []
        if options['organization_ids']:
            organization_ids = options['organization_ids']
        else:
            self.stdout.write('getting organizations with voters')
            organization_ids = getOrganizationsWithVoters(date_=date_of)

        for organization_id in organization_ids:
            setTfidfOfPG(self, organization_id)

        return 0
