from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from utils.delete_renders import delete_renders, refetch
from parlalize.utils_ import getAllStaticData
from parlaseje.views import getSessionsList
from parlaskupine.views import getListOfPGs
from parlaskupine.models import Organization
from parlaseje.models import Vote

from datetime import datetime, timedelta

import requests


class Command(BaseCommand):
    help = 'Delete all card renders'

    def handle(self, *args, **options):
        self.stdout.write('Refetch data')
        getAllStaticData(None, force_render=True)
        getSessionsList(None,force_render=True)
        for org in Organization.objects.filter(has_voters=True):
            getListOfPGs(None, str(org.id_parladata), force_render=True)
        requests.get(settings.FRONT_URL + '/api/data/refetch')
        requests.get(settings.GLEJ_URL + '/api/data/refetch')
        requests.get(settings.ISCI_URL + '/api/data/refetch')

        requests.get(settings.GLEJ_URL + '/api/cards/renders/delete/all?method=zakon')
        requests.get(settings.GLEJ_URL + '/api/cards/renders/delete/all?method=seznam-sej')
