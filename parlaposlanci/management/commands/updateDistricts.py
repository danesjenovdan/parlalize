from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, District
from parlalize.settings import API_URL, SETTER_KEY
from parlalize.utils_ import tryHard
from parlalize.utils_ import getDataFromPagerApi, getDataFromPagerApiGen
from utils.parladata_api import getAreas

class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/areas/' % API_URL)
        districts = getAreas(calssification="district")
        existing_districts = District.objects.all().values_list('id_parladata',
                                                                flat=True)
        for district in districts:
            if district['id'] not in existing_districts:
                self.stdout.write('Adding district %s' % str(district['id']))
                District(name=district['name'], id_parladata=district['id']).save()
            else:
                dist = District.objects.get(id_parladata=district['id'])
                if dist.name != district['name']:
                    self.stdout.write('Updating district %s' % str(district['id']))
                    dist.name = district['name']
                    dist.save()
                else:
                    self.stdout.write('Skipping district %s' % str(district['id']))
        return 0
