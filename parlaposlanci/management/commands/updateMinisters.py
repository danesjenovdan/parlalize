from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.views import setMinsterStatic
from parlalize.settings import API_URL, SETTER_KEY
from django.test.client import RequestFactory

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getIDsOfAllMinisters/' % API_URL)
        ministers = tryHard(API_URL + '/getIDsOfAllMinisters/').json()['ministers_ids']
        for ministr in ministers:
            self.stdout.write('Running setMinisterStatic on %s' % str(ministr))
            setMinsterStatic(request_with_key, str(ministr))

        return 0
