from django.core.management.base import BaseCommand, CommandError
from django.utils import dateparse

from parlalize.utils_ import tryHard, saveOrAbortNew, getDataFromPagerApiDRFGen
from parlalize.settings import API_URL, API_DATE_FORMAT
from parlaposlanci.models import Person, MPStaticPL, MPStaticGroup, District
from parlaskupine.models import Organization
from utils.parladata_api import getVotersPairsWithOrg, getPeople, getMemberships, getLinks

from datetime import datetime
from dateutil.relativedelta import relativedelta

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)


def num_years(begin, end=None):
    if end is None:
        end = datetime.now()
    num_years = int((end - begin).days / 365.25)
    if begin > yearsago(num_years, end):
        return num_years - 1
    else:
        return num_years


def setMPStaticPL(commander, person_id, date_=None):
    if not date_:
        date_of = datetime.now()

    commander.stdout.write('Fetching data from %s/persons/%s with day %s' % (API_URL, str(person_id), date_of))

    data = getPeople(id_=person_id)
    try:
        org_id = getVotersPairsWithOrg(date_=date_of)[int(person_id)]
    except Exception as e:
        commander.stdout.write('Person with ID %s has not correctly configured voter membership or he\'s not a MP' % str(person_id))
        commander.stdout.write(str(e))
        return

    organization = Organization.objects.get(id_parladata=org_id)

    person = Person.objects.get(id_parladata=int(person_id))

    socials ={'fb': 'facebook', 'tw': 'twitter', 'linkedin': 'linkedin'}
    social_objs = {}
    for key, name in socials.items():
        social_objs[name] = None
        for resp_data in getLinks(person=person_id, tags__name=key):
            if resp_data:
                social_objs[name] = resp_data['url']

    if not data:
        commander.stderr.write('Didn\'t get data.')
        raise CommandError('No data returned.')

    if 'error' in data.keys():
        commander.stderr.write('[API ERROR] %s' % data['error'])

    result = saveOrAbortNew(model=MPStaticPL,
                            created_for=date_of,
                            person=person,
                            voters=data['voters'],
                            points=data['points'],
                            age=num_years(dateparse.parse_datetime(data['birth_date'])) if data['birth_date'] else None,
                            birth_date=dateparse.parse_datetime(data['birth_date']) if data['birth_date'] else None,
                            mandates=data['mandates'],
                            party=organization,
                            education=data['education'],
                            education_level=data['education_level'],
                            previous_occupation=data['previous_occupation'],
                            name=data['name'],
                            district=data['districts'],
                            facebook=social_objs['facebook'],
                            twitter=social_objs['twitter'],
                            linkedin=social_objs['linkedin'],
                            party_name=organization.name,
                            acronym=organization.acronym,
                            gov_id=data['gov_id'],
                            gender='m' if data['gender'] == 'male' else 'f',
                            working_bodies_functions=[])

    commander.stdout.write('Set MP with id %s' % str(person_id))

class Command(BaseCommand):
    help = 'Updates MPs\' static data'

    def handle(self, *args, **options):
        memberships = getMemberships(role='voter')
        lastObject = {'members': {}}
        self.stdout.write('[info] update MP static')
        for membership in memberships:
            # call setters for members which have change in memberships
            setMPStaticPL(self, str(membership['person']), datetime.strptime(membership['start_time'], '%Y-%m-%dT%H:%M:%S'))
