from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization, PresenceThroughTime
from parlalize.utils_ import tryHard, saveOrAbortNew, getOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL, YES, NOT_PRESENT, AGAINST, ABSTAIN

def setPGPresenceThroughTime(commander, pg, date):
    if date:
        date_of = datetime.strptime(date, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()

    url = API_URL + '/getBallotsCounterOfParty/' + pg + '/' + date_of.strftime(API_DATE_FORMAT)
    data = tryHard(url).json()

    data_for_save = []

    for month in data:
        options = YES + NOT_PRESENT + AGAINST + ABSTAIN
        stats = sum([month[option] for option in options if option in month.keys()])
        presence = float(stats - sum([month[option] for option in NOT_PRESENT  if option in month.keys()])) / stats if stats else 0
        data_for_save.append({'date_ts': month['date_ts'],
                              'presence': presence * 100,
                              })

    org = Organization.objects.get(id_parladata=pg)
    commander.stdout.write('Saving presence for organization %s' % str(pg))
    saveOrAbortNew(model=PresenceThroughTime,
                           organization=org,
                           created_for=date_of,
                          data=data_for_save)

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
                date_ = datetime.strptime(options['date'], API_DATE_FORMAT)
            else:
                date_ = datetime.now()
            pgs = getOrganizationsWithVoters(date_=date_)

        for pg in pgs:
            setPGPresenceThroughTime(self, pg, options['date'])

        return 0