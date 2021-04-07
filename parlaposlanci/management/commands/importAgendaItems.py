from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import AgendaItem, Session
from django.conf import settings
from utils.parladata_api import getAgendaItems


class Command(BaseCommand):
    help = 'Sets session data'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/agenda-items/' % settings.API_URL)
        existingISs = list(AgendaItem.objects.all().values_list('id_parladata',
                                                            flat=True))
        data = getAgendaItems()
        for item in data:
            if int(item['id']) in existingISs:
                pass
            else:
                AgendaItem(
                    session=Session.objects.get(id_parladata=item['session']),
                    title=item['name'],
                    id_parladata=item['id']
                ).save()
