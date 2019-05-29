from django.core.management.base import BaseCommand, CommandError
from parlalize.settings import SETTER_KEY, API_DATE_FORMAT
from parlalize.utils_ import getParentOrganizationsWithVoters
from django.test.client import RequestFactory

from datetime import datetime, timedelta
from parlaposlanci.views import setListOfMembersTickers

# TODO refactor setListOfMembersTickers into this file
factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)


class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            #nargs='+',
            help='Date for which to run the card',
        )

    def handle(self, *args, **options):
        if options['date']:
            start_date = datetime.strptime(options['date'], API_DATE_FORMAT)
        else:
            start_date = datetime.now().date()

        #start_date = start_date - timedelta(days=1)
        for org_id in getParentOrganizationsWithVoters():
            setListOfMembersTickers(
                request_with_key,
                org_id,
                start_date.strftime(API_DATE_FORMAT),
            )
