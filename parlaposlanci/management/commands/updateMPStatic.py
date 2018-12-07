from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.views import setMPStaticPL
from django.test.client import RequestFactory
from parlalize.settings import API_URL, SETTER_KEY

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

class Command(BaseCommand):
    help = 'Updates MPs\' static data'

    def handle(self, *args, **options):
        memberships = tryHard(API_URL + '/getMembersOfPGsRanges/').json()
        lastObject = {'members': {}}
        self.stdout.write('[info] update MP static')
        for change in memberships:
            # call setters for new pg
            for pg in list(set(change['members'].keys()) - set(lastObject['members'].keys())):
                for member in change['members'][pg]:
                    self.stdout.write('About to run setMPStaticPL %s' % str(member))
                    setMPStaticPL(request_with_key, str(member), change['start_date'])

            # call setters for members which have change in memberships
            for pg in change['members'].keys():
                if pg in lastObject['members'].keys():
                    personsForUpdate = list(set(change['members'][pg]) - set(lastObject['members'][pg]))
                    for member in personsForUpdate:
                        self.stdout.write('About to run setMPStaticPL %s' % str(member))
                        setMPStaticPL(request_with_key, str(member), change['start_date'])
            lastObject = change