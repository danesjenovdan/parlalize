from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard, getDataFromPagerApi
from parlaposlanci.models import Person
from parlalize.settings import API_URL

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getAllPeople/' % API_URL)
        url = API_URL + '/getAllPeople/'
        data = getDataFromPagerApi(url)
        self.stdout.write('Fetching data from %s/getMPs/' % API_URL)
        mps = tryHard(API_URL + '/getMPs/').json()
        mps_ids = [mp['id'] for mp in mps]
        for mp in data:
            if Person.objects.filter(id_parladata=mp['id']):
                self.stdout.write('Updating person %d %s' % (mp['id'], mp['name']))
                person = Person.objects.get(id_parladata=mp['id'])
                person.name = mp['name']
                person.pg = mp['membership']
                person.id_parladata = int(mp['id'])
                person.image = mp['image']
                person.actived = True if int(mp['id']) in mps_ids else False
                person.gov_id = mp['gov_id']
                person.save()
            else:
                self.stdout.write('Adding person %d %s' % (mp['id'], mp['name']))
                is_active = True if int(mp['id']) in mps_ids else False
                person = Person(name=mp['name'],
                                pg=mp['membership'],
                                id_parladata=int(mp['id']),
                                image=mp['image'],
                                actived=is_active,
                                gov_id=mp['gov_id'])
                person.save()

        return 0