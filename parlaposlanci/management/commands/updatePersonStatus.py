from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlalize.settings import API_URL
from parlalize.utils_ import tryHard
from utils.parladata_api import getVotersIDs

class Command(BaseCommand):
    help = 'Update person status.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching  VotersIDs')
        mps_ids = getVotersIDs()
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
