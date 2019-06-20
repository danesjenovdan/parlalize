from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, MembershipsOfMember
from parlaskupine.models import Organization
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT
from utils.parladata_api import getVotersIDs


def setMembershipsOfMember(commander, person_id, date_=None):
    if date_:
        data = tryHard(API_URL+'/getMembershipsOfMember/' + person_id + "/" + date_).json()
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        data = tryHard(API_URL+'/getMembershipsOfMember/'+ person_id).json()
        date_of = datetime.now().date()

    person = Person.objects.get(id_parladata=int(person_id))

    saveOrAbortNew(MembershipsOfMember, created_for=date_of, person=person, data=data)

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
