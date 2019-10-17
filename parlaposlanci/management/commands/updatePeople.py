from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard, getDataFromPagerApi
from parlaposlanci.models import Person
from utils.parladata_api import getVotersPairsWithOrg, getPeople


class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from getVotersPairsWithOrg')
        mps_orgs = getVotersPairsWithOrg()
        data = getPeople()
        for mp in data:
            if mp['id'] in mps_orgs.keys():
                is_active = True
                org = mps_orgs[mp['id']]
            else:
                is_active = False
                org = ''
            if Person.objects.filter(id_parladata=mp['id']):
                self.stdout.write('Updating person %d %s' % (mp['id'], mp['name']))
                person = Person.objects.get(id_parladata=mp['id'])
                person.name = mp['name']
                person.pg = org
                person.id_parladata = int(mp['id'])
                person.image = mp['image']
                person.actived = is_active
                person.gov_id = mp['gov_id']
                person.save()
            else:
                self.stdout.write('Adding person %d %s' % (mp['id'], mp['name']))
                is_active = is_active
                person = Person(name=mp['name'],
                                pg=org,
                                id_parladata=int(mp['id']),
                                image=mp['image'],
                                actived=is_active,
                                gov_id=mp['gov_id'])
                person.save()

        return 0