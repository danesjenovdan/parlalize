from django.core.management.base import BaseCommand, CommandError

from parlalize.settings import API_URL, PARSER_UN, PARSER_PASS
from utils.delete_renders import delete_renders

from datetime import datetime

import requests

class Command(BaseCommand):
    help = 'Delete all card renders'

    def handle(self, *args, **options):
        self.stdout.write('Delete renders')
        delete_renders()
        return 0

