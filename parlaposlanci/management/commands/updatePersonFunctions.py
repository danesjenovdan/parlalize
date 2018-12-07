from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlalize.settings import API_URL
from parlalize.utils_ import tryHard

class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getMembersWithFunction/' % API_URL)
        mps = tryHard(API_URL + '/getMembersWithFunction/').json()

        for person in Person.objects.all():
            self.stdout.write('Updating person %s' % str(person.id_parladata))
            if person.has_function:
                if person.id_parladata not in mps['members_with_function']:
                    person.has_function = False
                    person.save()
            else:
                if person.id_parladata in mps['members_with_function']:
                    person.has_function = True
                    person.save()
        return 0
