from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Tag
from utils.parladata_api import getTags

class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from getTags')
        tags = getTags()
        existing_tags = Tag.objects.all().values_list('id_parladata', flat=True)
        for tag in tags:
            if tag['id'] not in existing_tags:
                #self.stdout.write('Adding tag %s' % str(tag['id']))
                Tag(name=tag['name'], id_parladata=tag['id']).save()
            else:
                #self.stdout.write('Skipping tag %s' % str(tag['id']))
                pass
        return 0
