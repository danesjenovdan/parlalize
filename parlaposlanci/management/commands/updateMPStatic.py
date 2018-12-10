from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, MPStaticPL, MPStaticGroup
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from django.utils import dateparse
from parlalize.settings import API_URL, API_DATE_FORMAT


def setMPStaticPL(commander, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        commander.stdout.write('Fetching data from %s/getMPStatic/%s/%s with date' % (API_URL, str(person_id), str(date_)))
        data = tryHard(API_URL + '/getMPStatic/' + person_id + "/" + date_).json()
    else:
        date_of = datetime.now().date()
        commander.stdout.write('Fetching data from %s/getMPStatic/%s/%s with today' % (API_URL, str(person_id), str(date_)))
        data = tryHard(API_URL + '/getMPStatic/' + person_id).json()

    person = Person.objects.get(id_parladata=int(person_id))
    if not data:
        commander.stderr.write('Didn\'t get data.')
        raise CommandError('No data returned.')

    if 'error' in data.keys():
        commander.stderr.write('[API ERROR] %s' % data['error'])

    result = saveOrAbortNew(model=MPStaticPL,
                            created_for=date_of,
                            person=person,
                            voters=data['voters'],
                            age=data['age'],
                            birth_date=dateparse.parse_datetime(data['birth_date']) if data['birth_date'] else None,
                            mandates=data['mandates'],
                            party=Organization.objects.get(id_parladata=int(data['party_id'])),
                            education=data['education'],
                            education_level=data['education_level'],
                            previous_occupation=data['previous_occupation'],
                            name=data['name'],
                            district=data['district'],
                            facebook=data['social']['facebook'],
                            twitter=data['social']['twitter'],
                            linkedin=data['social']['linkedin'],
                            party_name=data['party'],
                            acronym=data['acronym'],
                            gov_id=data['gov_id'],
                            gender=data['gender'],
                            working_bodies_functions=data['working_bodies_functions'])

    if result:
        for group in data['groups']:
            new_group = MPStaticGroup(person=MPStaticPL.objects.filter(person__id_parladata=int(person_id)).latest('created_at'), groupid=int(group['id']), groupname=group['name'])
            new_group.save()

    commander.stdout.write('Set MP with id %s' % str(person_id))

class Command(BaseCommand):
    help = 'Updates MPs\' static data'

    def handle(self, *args, **options):
        memberships = tryHard(API_URL + '/getMembersOfPGsRanges/').json()
        lastObject = {'members': {}}
        self.stdout.write('[info] update MP static')
        for change in memberships:
            # call setters for new pg
            for pg in list(set(change['members'].keys()) - set(lastObject['members'].keys())):
                for member in change['members'][pg]:
                    self.stdout.write('About to run setMPStaticPL %s' % str(member))
                    setMPStaticPL(self, str(member), change['start_date'])

            # call setters for members which have change in memberships
            for pg in change['members'].keys():
                if pg in lastObject['members'].keys():
                    personsForUpdate = list(set(change['members'][pg]) - set(lastObject['members'][pg]))
                    for member in personsForUpdate:
                        self.stdout.write('About to run setMPStaticPL %s' % str(member))
                        setMPStaticPL(self, str(member), change['start_date'])
            lastObject = change