import json

from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization, PGStatic
from parlalize.utils import tryHard, saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL

def setBasicInfoOfPG(commander, pg, date):
    if date:
        date_of = datetime.strptime(date, API_DATE_FORMAT).date()
        url = API_URL + '/getBasicInfOfPG/' + str(pg) + '/' + date
        commander.stdout.write('Trying hard for %s' % url)
        data = tryHard(url).json()
    else:
        date_of = datetime.now().date()
        url = API_URL+'/getBasicInfOfPG/' + str(pg) + '/'
        commander.stdout.write('Trying hard for %s' % url)
        data = tryHard(url).json()

    headOfPG = 0
    viceOfPG = []
    if data['HeadOfPG'] is not None:
        commander.stdout.write('Defiing head of PG')
        headOfPG = Person.objects.get(id_parladata=int(data['HeadOfPG']))
    else:
        commander.stdout.write('No head of PG')
        headOfPG = None

    if data['ViceOfPG']:
        for vice in data['ViceOfPG']:
            if vice is not None:
                viceOfPG.append(vice)
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
                  numberOfSeats=data['NumberOfSeats'],
                  allVoters=data['AllVoters'],
                  facebook=json.dumps(data['Facebook']),
                  twitter=json.dumps(data['Twitter']),
                  email=data['Mail']
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
            else:
                date_ = datetime.now().date().strftime(API_DATE_FORMAT)
            self.stdout.write('Trying hard for %s/getMembersOfPGsOnDate/%s' % (API_URL, str(options['date'])))
            membersOfPGsRanges = tryHard(API_URL + '/getMembersOfPGsRanges/' + str(options['date'])).json()
            pgs = [key for key, value in membersOfPGsRanges[-1]['members'].items() if value]

        for pg in pgs:
            setBasicInfoOfPG(self, pg, options['date'])

        return 0