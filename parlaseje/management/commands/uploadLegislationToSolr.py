# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Legislation
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json


class Command(BaseCommand):
    help = 'Upload legislation to Solr'

    def commit_to_solr(self, output):
        url = SOLR_URL + '/update?commit=true'
        self.stdout.write('About to commit %s legislations to %s' % (str(len(output)), url))
        data = json.dumps(output)
        requests.post(url,
                      data=data,
                      headers={'Content-Type': 'application/json'})

    def handle(self, *args, **options):
        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        # get all legislations
        self.stdout.write('Getting legislations')
        legislations = Legislation.objects.all()

        i = 1
        output = []
        for legislation in legislations:
            sessions = list(legislation.sessions.all().values_list('id_parladata', flat=True))
            note = legislation.note
            if note:
                note = strip_tags(note).replace("&nbsp;", " ").replace("\r", "").replace("\n", " ").replace("&scaron;", "š")

            output.append({
                'term': 'VIII',
                'type': 'legislation',
                'id': 'legislation_' + str(legislation.id_parladata),
                'act_id': legislation.epa,
                'sessions': sessions,
                'content': note,
                'title': legislation.text,
                'status': legislation.status,
                # 'result': legislation.result, # TODO: this is duplicated from status, remove for now
                'wb': legislation.mdt,
            })

            if i % 100 == 0:
                self.commit_to_solr(output)
                output = []

            i += 1

        if len(output):
            self.commit_to_solr(output)

        return 0
