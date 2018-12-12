# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Legislation
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json

class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def handle(self, *args, **options):
        i = 0
        output = []
        self.stdout.write('Beginning legislation export ...')
        for legislation in Legislation.objects.all():
            i += 1
            sessions = list(map(str, list(legislation.sessions.all().values_list('id_parladata', flat=True))))
            note = legislation.note
            if note:
                note = strip_tags(note).replace("&nbsp;", "").replace("\r", "").replace("\n", "").replace("&scaron;", "š")
            output.append({
                'id': legislation.epa,
                'sessions_i': sessions,
                'mdt': legislation.mdt,
                'text_t': legislation.text,
                'content_t': note,
                'status': legislation.status,
                'result': legislation.result,
                'sklic_t': legislation.epa.split('-')[1],
                'tip_t': 'l'
            })

            

            if i % 100 == 0:
                data = json.dumps(output)
                self.stdout.write('About to commit another 100 pieces of legislation to %s/update?commit=true' % SOLR_URL)
                requests.post(SOLR_URL + '/update?commit=true',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
                output = []

        self.stdout.write('Final legislation commit to %s/update?commit=true' % SOLR_URL)
        data = json.dumps(output)
        r = requests.post(SOLR_URL + '/update?commit=true',
                          data=data,
                          headers={'Content-Type': 'application/json'})

        self.stdout.write(str(r.text))

        return 0