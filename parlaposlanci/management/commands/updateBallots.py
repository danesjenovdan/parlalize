from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Ballot, Vote
from parlaposlanci.models import Person
from parlalize.settings import API_URL, SETTER_KEY
from django.test.client import RequestFactory
from parlalize.utils_ import getDataFromPagerApi, getDataFromPagerApiGen

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from  %s/ballots/' % API_URL)
        existingISs = Ballot.objects.all().values_list('id_parladata', flat=True)
        for page in getBallots():
            for dic in page:
                if int(dic['id']) not in existingISs:
                    self.stdout.write('Adding ballot %s' % str(dic['vote']))
                    vote = Vote.objects.get(id_parladata=dic['vote'])
                    person = Person.objects.get(id_parladata=int(dic['voter']))
                    ballots = Ballot(option=dic['option'],
                                     vote=vote,
                                     start_time=vote.start_time,
                                     end_time=None,
                                     id_parladata=dic['id'],
                                     voter_party = Organization.objects.get(id_parladata=dic['voterparty']))
                    ballots.save()
                    ballots.person.add(person)
                else:
                    b = Ballot.objects.get(id_parladata=dic['id'])
                    b.voter_party = Organization.objects.get(id_parladata=dic['voterparty'])
                    b.save()
        return 0
