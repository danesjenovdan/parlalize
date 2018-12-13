from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Vote
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json

class Command(BaseCommand):
    help = 'Upload votes to Solr'

    def handle(self, *args, **options):
        votes = Vote.objects.all()

        i = 0

        for vote in votes:
            output = [{
                'id': 'v' + str(vote.id_parladata),
                # 'motionid_i': str(vote.motion.id),
                'voteid_i': str(vote.id_parladata),
                'content_t': vote.motion,
                'sklic_t': 'VIII',
                'tip_t': 'v'
            }]

            output = json.dumps(output)

            if i % 100 == 0:
                r = requests.post(SOLR_URL + '/update?commit=true',
                                  data=output,
                                  headers={'Content-Type': 'application/json'})

                print r.text

            else:
                r = requests.post(SOLR_URL + '/update',
                                  data=output,
                                  headers={'Content-Type': 'application/json'})

            i = i + 1

        return 0