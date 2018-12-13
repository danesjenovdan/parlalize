from django.core.management.base import BaseCommand, CommandError
from utils.compass import getData as getCompassData
from parlaposlanci.models import Compass
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT


class Command(BaseCommand):
    help = 'Updates compas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='PG parladata_ids',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_of = datetime.strptime(options['date'], API_DATE_FORMAT).date()
        else:
            date_of = datetime.now().date()
        data = getCompassData(date_of)
        if data == []:
            self.stdout.write('No data for compass')
            return
        #print data
        existing_compas = Compass.objects.filter(created_for=date_of)
        if existing_compas:
            existing_compas[0].data = data
            existing_compas[0].save()
        else:
            Compass(created_for=date_of,
                    data=data).save()
        self.stdout.write('Compass was set.')
        return 0
