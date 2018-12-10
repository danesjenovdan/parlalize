from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, MinisterStatic
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT


def setMinsterStatic(commander, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        m_data = tryHard(API_URL+'/getMinistrStatic/' + person_id + "/" + date_).json()
    else:
        date_of = datetime.now().date()
        m_data = tryHard(API_URL+'/getMinistrStatic/' + person_id).json()

    if not m_data:
    	commander.stdout.write('Didn\'t get data of minsiter with id: %s' % str(person_id))
    	raise CommandError('No data returned.')
  
    person = Person.objects.get(id_parladata=int(person_id))

    for data in m_data:
        start_time = data['start_time'].split('T')[0]
        if data['party']:
            party = Organization.objects.get(id_parladata=data['party']['id'])
        else:
            party = None

        if data['ministry']:
            ministry = Organization.objects.get(id_parladata=data['ministry']['id'])
        else:
            ministry = None

        ministry_static = MinisterStatic.objects.filter(person=person,
                                                        ministry=ministry,
                                                        created_for=start_time)
        if ministry_static:
            # TODO: edit?
            pass
        else:
            MinisterStatic(created_for=start_time,
                           person=person,
                           age=data['age'],
                           party=party,
                           education=data['education'],
                           previous_occupation=data['previous_occupation'],
                           name=data['name'],
                           district=data['district'],
                           facebook=data['social']['facebook'],
                           twitter=data['social']['twitter'],
                           linkedin=data['social']['linkedin'],
                           gov_id=data['gov_id'],
                           gender=data['gender'],
                           ministry=ministry).save()

    commander.stdout.write('Set minister with id %s' % str(person_id))


class Command(BaseCommand):
    help = 'Updates ministers from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getIDsOfAllMinisters/' % API_URL)
        ministers = tryHard(API_URL + '/getIDsOfAllMinisters/').json()['ministers_ids']
        for ministr in ministers:
            self.stdout.write('Running setMinisterStatic on %s' % str(ministr))
            setMinsterStatic(self, str(ministr))

        return 0
