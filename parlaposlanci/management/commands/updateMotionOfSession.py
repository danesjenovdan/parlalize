from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Session
from parlalize.settings import API_URL, DZ, SETTER_KEY
from parlaseje.views import setMotionOfSession
from django.test.client import RequestFactory

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def handle(self, *args, **options):
      ses = Session.objects.all()
      for s in ses:
          self.stdout.write('Updating session %s' % str(s.id_parladata))
          resp =  setMotionOfSession(request_with_key, str(s.id_parladata))
          self.stdout.write(resp.content)
      
      return 0
