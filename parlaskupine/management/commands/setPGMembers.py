from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, MPOfPg
from parlalize.settings import API_DATE_FORMAT
from parlalize.utils_ import saveOrAbortNew, tryHard
from utils.parladata_api import getOrganizationsWithVoters, getVotersPairsWithOrg
from datetime import datetime

def setMPsOfPG(commander, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        commander.stdout.write('Setting for date %s' % str(date_of))
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
        commander.stdout.write('Setting for today (%s)' % str(date_of))

    pairs = getVotersPairsWithOrg()
    membersOfPG = {i: []for i in set(pairs.values())}
    for mem, org in pairs.items():
        membersOfPG[org].append(mem)
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
        date_ = date_of.strftime(API_DATE_FORMAT)

        pgs = []

        if options['pgs']:
            pgs = options['pgs']
        else:
            pgs = getOrganizationsWithVoters(date_=date_of)

        for pg in pgs:
            self.stdout.write('About to set MPS of %s' % str(pg))
            setMPsOfPG(self, pg)

        return 0