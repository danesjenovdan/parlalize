from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, AverageNumberOfSpeechesPerSession
from parlalize.utils_ import saveOrAbortNew, tryHard
from utils.compass import getData as getCompassData
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL


class Command(BaseCommand):
    help = 'Updates compas'

    def handle(self, *args, **options):
        if date_:
            date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        else:
            date_of = datetime.now().date()
            date_ = date_of.strftime(API_DATE_FORMAT)
        data = getCompassData(date_of)
        if data == []:
            commander.stdout.write('No data for compass')
            return
        #print data
        existing_compas = Compass.objects.filter(created_for=date_of)
        if existing_compas:
            existing_compas[0].data = data
            existing_compas[0].save()
        else:
            Compass(created_for=date_of,
                    data=data).save()
        commander.stdout.write('Compass was set.')
        return 0
