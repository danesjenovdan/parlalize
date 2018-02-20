# -*- coding: utf-8 -*-
from parlaseje.models import Legislation
from parlaposlanci.models import *
from parlalize.utils_ import tryHard, getPersonCardModelNew

from django.conf import settings
from django.utils.html import strip_tags

from datetime import datetime

import requests
import json
import csv

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
            'status': legislation.status,
            'result': legislation.result,
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


def deleteLegislations():
    a = requests.get(settings.SOLR_URL + "/select?wt=json&q=id:*&fl=id&fq=tip_t:l&rows=100000000")
    indexes = a.json()["response"]["docs"]
    idsForDelete = [idx['id'] for idx in indexes]
    data = {'delete': idsForDelete
            }

    r = requests.post(settings.SOLR_URL + '/update?commit=true',
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})

    print r.text
    return True



def backupNotes():
    data = {}
    file_name = 'notes/notes' + datetime.now().strftime('%d_%m_%Y') + '.json'
    f = open(file_name, 'w')
    for leg in Legislation.objects.all():
        if leg.note:
            data[leg.epa] = leg.note

    f.write(json.dumps(data))
    f.close()



def listToCSV(data, file_name):
    with open(file_name, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)

        if type(data[0]) == dict:
             csvwriter.writerow(data[0].keys())
        for value in data:
            if type(value) == list:
                e_data = value
            elif type(value) == tuple:
                e_data = list(value)
            elif type(value) == dict:
                e_data = value.values()
            else:
                e_data = [value.values]
            csvwriter.writerow(e_data)
    return file_name


def data_to_csv():
    models = [(Presence, 'prisotnost na glasovanjih sej DZ'),
              (NumberOfQuestions, 'st. poslanskih vprasanj in pobud'),
              (MismatchOfPG, 'neujemanje s poslansko skupino'),
              (SpokenWords, 'st. izgovorjenih besed'),
              (AverageNumberOfSpeechesPerSession, 'stevilo govorov na sejo'),
              (VocabularySize, 'raznolikost besedisca')]

    mps = tryHard(settings.API_URL+'/getMPs/').json()

    data = []

    for mp in mps:
        tmp = {'member_id': mp['id']}
        for model, column in models:
            print mp['id'], model
            model_data = getPersonCardModelNew(model, mp['id'])
            if model == Presence:
                tmp[column] = model_data.person_value_sessions
                tmp[column] = model_data.person_value_votes
            if model == NumberOfQuestions or model == SpokenWords or model == VocabularySize:
                tmp[column] = model_data.score
            if model == MismatchOfPG:
                tmp[column] = model_data.data
            if model == NumberOfSpeechesPerSession:
                tmp[column] = model_data.person_value
        data.append(tmp)
    listToCSV(data, 'toski_export.csv')
data_to_csv()