from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Tag
from parlalize.settings import API_URL
from parlalize.utils_ import tryHard

class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/getTags/' % API_URL)
        tags = tryHard(API_URL+'/getTags/').json()
        existing_tags = Tag.objects.all().values_list('id_parladata', flat=True)
        for tag in tags:
            if tag['id'] not in existing_tags:
                self.stdout.write('Adding tag %s' % str(tag['id']))
                Tag(name=tag['name'], id_parladata=tag['id']).save()
            else:
                self.stdout.write('Skipping tag %s' % str(tag['id']))
        return 0
