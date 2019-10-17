from django.core.management.base import BaseCommand, CommandError

from utils.delete_renders import delete_renders, refetch

from datetime import datetime


class Command(BaseCommand):
    help = 'Delete all card renders'

    def handle(self, *args, **options):
        self.stdout.write('Refetch data')
        refetch()
        self.stdout.write('Delete renders')
        delete_renders()
        return 0
