from django.core.management.base import BaseCommand, CommandError
from parlalize.settings import SETTER_KEY, API_DATE_FORMAT
from django.test.client import RequestFactory

from datetime import datetime, timedelta
from parlaposlanci.views import setListOfMembersTickers

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date from',
        )

    def handle(self, *args, **options):
        start_date = datetime.strptime(options['date'][0], '%Y-%m-%dT%X')
        start_date = start_date - timedelta(days=1)
        setListOfMembersTickers(request_with_key, start_date.strftime(API_DATE_FORMAT))
