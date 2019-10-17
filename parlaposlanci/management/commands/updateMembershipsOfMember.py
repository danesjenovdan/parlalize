from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, MembershipsOfMember
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT
from utils.parladata_api import getVotersIDs, getOrganizations, getMembershipsOfMember, getLinks
from collections import defaultdict



def setMembershipsOfMember(commander, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()

    organizations = {org['id']: org for org in getOrganizations()}
    memberships = getMembershipsOfMember(person_id=person_id, date_=date_of)
    data = defaultdict(list)

    person = Person.objects.get(id_parladata=int(person_id))

    for mem in memberships:
        organization = organizations[mem['organization']]
        org_links = getLinks(organization=organization['id'])
        if org_links:
            org_link = org_links[0]['url']
        else:
            org_link = None
        data[organization['classification']].append(
            {
                'url': org_link,
                'org_type': organization['classification'],
                'org_id': organization['id'],
                'name': organization['_name']
            }
        )

    saveOrAbortNew(MembershipsOfMember, created_for=date_of, person=person, data=dict(data))

    commander.stdout.write('Set MembershipsOfMember for person id %s' % str(person_id))


class Command(BaseCommand):
    help = 'Updates ministers from Parladata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='PG parladata_ids',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_of = datetime.strptime(options['date'], API_DATE_FORMAT).date()
            date_ = options['date']
        else:
            # dirty work around, TODO: fix findDatesFromLastCard for input without person_id
            #date_of = findDatesFromLastCard(Presence, '11', datetime.now().strftime(API_DATE_FORMAT))[0]
            date_of = datetime.now().date()
            date_ = date_of.strftime(API_DATE_FORMAT)

        self.stdout.write('Getting voters')
        for mp in getVotersIDs(date_=date_of):
            self.stdout.write('Running setMembershipsOfMember on %s' % str(mp))
            setMembershipsOfMember(self, str(mp), date_)

        return 0
