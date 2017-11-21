from parlaseje.models import Legislation

from django.conf import settings

import requests


def exportLegislations():
    i = 0
    output = []
    for legislation in Legislation.objects.all():
        sessions = list(map(str, list(legislation.sessions.all().values_list('id_parladata', flat=True))))
        output.append({
            'id': legislation.epa,
            'sessions_i': sessions,
            'mdt': legislation.mdt,
            'text_t': legislation.text,
            'content_t': legislation.note,
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