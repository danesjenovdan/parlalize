from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaskupine.models import Organization
from parlalize.settings import API_URL

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getAllOrganizations' % API_URL)
        data = tryHard(API_URL + '/getAllOrganizations').json()
        for pg in data:
            if Organization.objects.filter(id_parladata=pg):
                self.stdout.write('Updating organisation %s' % str(pg))
                org = Organization.objects.get(id_parladata=pg)
                org.name = data[pg]['name']
                org.classification = data[pg]['classification']
                org.acronym = data[pg]['acronym']
                org.is_coalition = data[pg]['is_coalition']
                org.save()
            else:
                self.stdout.write('Adding organisation %s' % str(pg))
                org = Organization(name=data[pg]['name'],
                                  classification=data[pg]['classification'],
                                  id_parladata=pg,
                                  acronym=data[pg]['acronym'],
                                  is_coalition=data[pg]['is_coalition'])
                org.save()
        return 0