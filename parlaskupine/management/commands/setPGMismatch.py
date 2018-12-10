from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import MismatchOfPG
from parlaskupine.models import Organization, PGMismatch
from parlalize.utils_ import tryHard, saveOrAbortNew, getAllStaticData, getPersonCardModelNew
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL, YES, NOT_PRESENT, AGAINST, ABSTAIN

def setPGMismatch(commander, pg_id, date=None):
    """
    Setter for analysis mismatch of parlament group
    """
    if date:
        date_of = datetime.strptime(date, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()
        date = ''

    org = Organization.objects.get(id_parladata=pg_id)
    url = API_URL + '/getMembersOfPGsOnDate/' + date
    commander.stdout.write('Trying hard with %s' % url)
    memsOfPGs = tryHard(url).json()
    data = []
    for member in memsOfPGs[str(pg_id)]:
        try:
            mismatch = getPersonCardModelNew(MismatchOfPG, int(member), date)
            data.append({'id': member,
                     'ratio': mismatch.data})
        except:
            commander.stderr.write('No MismatchOfPG card for person %s' % str(member))
            pass
    
    saveOrAbortNew(model=PGMismatch,
                  organization=org,
                  created_for=date_of,
                  data=data)
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
            self.stdout.write('Trying hard for %s/getMembersOfPGsOnDate/%s' % (API_URL, date_))
            membersOfPGsRanges = tryHard(API_URL + '/getMembersOfPGsRanges/' + date_).json()
            pgs = [key for key, value in membersOfPGsRanges[-1]['members'].items() if value]

        for pg in pgs:
            setPGMismatch(self, pg, options['date'])

        return 0