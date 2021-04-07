from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaskupine.models import Organization
from django.conf import settings
from utils.parladata_api import getOrganizations

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/organizations/' % settings.API_URL)
        data = getOrganizations()
        for pg in data:
            if Organization.objects.filter(id_parladata=pg['id']):
                self.stdout.write('Updating organisation %s' % str(pg['id']))
                org = Organization.objects.get(id_parladata=pg['id'])
                org.name = pg['name']
                org.classification = pg['classification']
                org.acronym = pg['acronym']
                org.name_parser = pg['name_parser']
                org.is_coalition = True if pg['is_coalition'] else False
                org.save()
            else:
                self.stdout.write('Adding organisation %s' % str(pg['id']))
                org = Organization(name=pg['name'],
                                  classification=pg['classification'],
                                  id_parladata=pg['id'],
                                  acronym=pg['acronym'],
                                  is_coalition=True if pg['is_coalition'] else False)
                org.save()
        return 0
