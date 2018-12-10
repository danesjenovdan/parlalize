from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlalize.settings import API_URL
from parlalize.utils_ import tryHard

class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getMPs/' % API_URL)
        mps = tryHard(API_URL + '/getMPs/').json()
        mps_ids = [mp['id'] for mp in mps]
        for person in Person.objects.all():
            self.stdout.write('Updating person %s' % str(person.id_parladata))
            if person.actived == 'Yes':
                if person.id_parladata not in mps_ids:
                    person.actived = 'No'
                    person.save()
            else:
                if person.id_parladata in mps_ids:
                    person.actived = 'Yes'
                    person.save()
        return 0
