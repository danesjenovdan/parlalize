from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaskupine.models import Organization
from parlalize.settings import API_URL
from utils.parladata_api import getOrganizations

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/organizations/' % API_URL)
        data = getOrganizations()
        for pg in data:
            if Organization.objects.filter(id_parladata=pg):
                self.stdout.write('Updating organisation %s' % str(pg))
                org = Organization.objects.get(id_parladata=pg)
                org.name = data[pg]['name']
                org.classification = data[pg]['classification']
                org.acronym = data[pg]['acronym']
                org.name_parser = data[pg]['name_parser']
                org.is_coalition = True if data[pg]['is_coalition'] else False
                org.save()
            else:
                self.stdout.write('Adding organisation %s' % str(pg))
                org = Organization(name=data[pg]['name'],
                                  classification=data[pg]['classification'],
                                  id_parladata=pg,
                                  acronym=data[pg]['acronym'],
                                  is_coalition=True if data[pg]['is_coalition'] else False)
                org.save()
        return 0