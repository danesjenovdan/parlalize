from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT
from utils.votes import VotesAnalysis
from utils.parladata_api import getParentOrganizationsWithVoters

class Command(BaseCommand):
    help = 'Updates compas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date for which to run analyses',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_ = options['date']
        else:
            date_ = datetime.now().date().strftime(API_DATE_FORMAT)
        for org_id in getParentOrganizationsWithVoters():
            votes = VotesAnalysis(organization_id=org_id, datetime.strptime(date_, API_DATE_FORMAT))
            self.stdout.write('About to begin VotesAnalysis for %s' % str(date_))
            votes.setAll()
            self.stdout.write('Done with VotesAnalysis for %s' % str(date_))

        return 0