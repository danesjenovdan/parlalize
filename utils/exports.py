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
              (VocabularySize, 'raznolikost besedisca'),
              (MPStaticPL, 'st_mandatov')]

    mps = tryHard(settings.API_URL+'/getMPs/').json()

    data = []

    for mp in mps:
        tmp = {'member_id': mp['id'], 'ime': mp['name'], 'PS': mp['acronym']}
        for model, column in models:
            print mp['id'], model
            model_data = getPersonCardModelNew(model, mp['id'])
            if model == Presence:
                tmp[column] = model_data.person_value_votes
            if model == NumberOfQuestions or model == SpokenWords or model == VocabularySize:
                tmp[column] = model_data.score
            if model == MismatchOfPG:
                tmp[column] = model_data.data
            if model == NumberOfSpeechesPerSession:
                tmp[column] = model_data.person_value
            if model == MPStaticPL:
                tmp[column] = model_data.mandates
                tmp['izobrazba'] = model_data.education_level
        data.append(tmp)
    listToCSV(data, 'toski_export.csv')
