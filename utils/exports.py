# -*- coding: utf-8 -*-
from parlaseje.models import Legislation

from django.conf import settings
from django.utils.html import strip_tags

from datetime import datetime

import requests
import json

def exportLegislations():
    i = 0
    output = []
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
            'sklic_t': legislation.epa.split('-')[1],
            'tip_t': 'l'
        })

        

        if i % 100 == 0:
            data = json.dumps(output)
            r = requests.post(settings.SOLR_URL + '/update?commit=true',
                              data=data,
                              headers={'Content-Type': 'application/json'})
            output = []

            print r.text
    data = json.dumps(output)
    r = requests.post(settings.SOLR_URL + '/update?commit=true',
                              data=data,
                              headers={'Content-Type': 'application/json'})

    print r.text

    return 1


def backupNotes():
    data = {}
    file_name = 'notes/notes' + datetime.now().strftime('%d_%m_%Y') + '.json'
    f = open(file_name, 'w')
    for leg in Legislation.objects.all():
        if leg.note:
            data[leg.epa] = leg.note

    f.write(json.dumps(data))
    f.close()

