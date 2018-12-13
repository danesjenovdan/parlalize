from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT
from utils.votes_pg import set_mismatch_of_pg

class Command(BaseCommand):
    help = 'Updates deviation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date for which to run the card',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_ = options['date']
        else:
            date_ = datetime.now().date().strftime(API_DATE_FORMAT)

        # TODO refactor votes_pg.py to stop accepting request as an argument
        set_mismatch_of_pg(None, date_)

        return 0