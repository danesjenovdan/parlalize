import json

from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization, PGStatic
from parlalize.utils_ import tryHard, saveOrAbortNew
from utils.parladata_api import getOrganizationsWithVoters, getOrganizations, getContactDetails, getVotersPairsWithOrg, getLinks, getPosts
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT
from collections import Counter

def setBasicInfoOfPG(commander, pg, date):
    if date:
        date_of = datetime.strptime(date, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()

    org_data = getOrganizations(pg)
    contacts = getContactDetails(organization=pg)

    president = getPosts(date_of, organization=pg, role="president")
    deputy = getPosts(date_of, organization=pg, role="deputy")

    email = ''
    for contact in contacts:
        if contact['contact_type'] == 'EMAIL':
            email = contact['value']

    facebook = [link['url'] for link in getLinks(organization=pg, tags__name='fb')]
    twitter = [link['url'] for link in getLinks(organization=pg, tags__name='tw')]

    numberOfSeats = dict(Counter(getVotersPairsWithOrg(date_=date_of).values()))[int(pg)]

    headOfPG = None
    viceOfPG = []
    if president:
        commander.stdout.write('Defiing head of PG')
        headOfPG = Person.objects.get(id_parladata=int(president[0]['person']))
    else:
        commander.stdout.write('No head of PG')
        headOfPG = None

    if deputy:
        for vice in deputy:
            if vice:
                viceOfPG.append(vice['person'])
            else:
                viceOfPG.append(None)
    else:
                viceOfPG.append(None)
    org = Organization.objects.get(id_parladata=int(pg))
    commander.stdout.write('Saving organization %s' % str(pg))
    saveOrAbortNew(model=PGStatic,
                  created_for=date_of,
                  organization=org,
                  headOfPG=headOfPG,
                  viceOfPG=viceOfPG,
                  numberOfSeats=numberOfSeats,
                  allVoters=org_data['voters'],
                  facebook=json.dumps(facebook) if facebook else None,
                  twitter=json.dumps(twitter) if twitter else None,
                  email=email
                  )

    return


class Command(BaseCommand):
    help = 'Updates compas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date for which to run the card',
        )

        parser.add_argument(
            '--pgs',
            nargs='+',
            help='PG parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        if options['pgs']:
            pgs = options['pgs']
        else:
            if options['date']:
                date_ = options['date']
                date_of = datetime.strptime(date_, API_DATE_FORMAT)
            else:
                date_of = datetime.now()
            pgs = getOrganizationsWithVoters(date_=date_of)

        for pg in pgs:
            setBasicInfoOfPG(self, pg, options['date'])

        return 0
