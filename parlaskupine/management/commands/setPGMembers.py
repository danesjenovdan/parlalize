from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, MPOfPg
from parlalize.settings import API_DATE_FORMAT, API_URL
from parlalize.utils_ import saveOrAbortNew, tryHard
from datetime import datetime

def setMPsOfPG(commander, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        commander.stdout.write('Setting for date %s' % str(date_of))
    else:
        date_of = datetime.now().date()
        date_ = datetime.now().date()
        commander.stdout.write('Setting for today (%s)' % str(date_of))

    commander.stdout.write('Trying hard for %s/getMembersOfPGsOnDate/%s' % (API_URL, str(date_of)))
    membersOfPG = tryHard(API_URL+'/getMembersOfPGsOnDate/' + date_).json()
    org = Organization.objects.get(id_parladata=pg_id)
    commander.stdout.write('Setting for organisation %s' % str(pg_id))
    saveOrAbortNew(model=MPOfPg,
                  organization=org,
                  id_parladata=pg_id,
                  MPs=membersOfPG[pg_id],
                  created_for=date_of
                  )

class Command(BaseCommand):
    help = 'Update districts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pgs',
            nargs='+',
            help='PG parladata_ids',
            type=int,
        )

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = datetime.now().date()

        if options['pgs']:
            if len(options['pgs']) > 0:
                pgs = options['pgs']
            else:
                self.stdout.write('Trying hard for %s/getMembersOfPGsOnDate/%s' % (API_URL, str(date_of)))
                membersOfPGsRanges = tryHard(API_URL + '/getMembersOfPGsRanges/' + date_).json()
                pgs = [key for key, value in membersOfPGsRanges[-1]['members'].items() if value]

        for pg in pgs:
            self.stdout.write('About to set MPS of %s' % str(pg_id))
            setMPsOfPG(self, pg)

        return 0