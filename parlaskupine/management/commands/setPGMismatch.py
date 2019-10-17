from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import MismatchOfPG
from parlaskupine.models import Organization, PGMismatch
from parlalize.utils_ import tryHard, saveOrAbortNew, getAllStaticData, getPersonCardModelNew
from utils.parladata_api import getOrganizationsWithVoters, getOrganizationsWithVotersList
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, YES, NOT_PRESENT, AGAINST, ABSTAIN

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
    memsOfPGs = getOrganizationsWithVotersList(date_=date_of)
    data = []
    for member in memsOfPGs[int(pg_id)]:
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
                date_ = datetime.strptime(options['date'], API_DATE_FORMAT)
            else:
                date_ = datetime.now()
            pgs = getOrganizationsWithVoters(date_=date_)

        for pg in pgs:
            setPGMismatch(self, pg, options['date'])

        return 0
