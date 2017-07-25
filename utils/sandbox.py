# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime, timedelta
import time
import requests


def createCompasData():
    API_ENDPOINT = 'https://analize.parlameter.si/v1/p/getCompass/'
    DATE_FORMAT = '%d.%m.%Y'
    START_DATE = datetime.strptime('25.8.2014', DATE_FORMAT)
    DAY_COUNT = (datetime.today() - START_DATE).days

    days = []

    for day in (START_DATE + timedelta(n) for n in range(DAY_COUNT)):
        print API_ENDPOINT + datetime.strftime(day, DATE_FORMAT)
        days.append(requests.get(API_ENDPOINT + datetime.strftime(day, DATE_FORMAT)).json())

    with open('data.json', 'w') as outfile:
        json.dump(days, outfile)

    # data.json je prevelik
    infile = open('data.json', 'r')
    days = json.load(infile)

    iterated_days = []
    filtered_days = []
    for day in days:
        if day['created_for'] not in iterated_days:
            iterated_days.append(day['created_for'])
            filtered_days.append(day)

    with open('filtered_data.json', 'w') as outfile:
        json.dump(filtered_days, outfile)

    # data.json še vedno prevelik
    infile = open('filtered_data.json', 'r')
    days = json.load(infile)

    clean_days = []
    for day in days:
        clean_days.append({'date': day['created_for'],
                           'people': [{'id': person['person']['id'],
                                       'vT1': person['score']['vT1'],
                                       'vT2': person['score']['vT2']}
                                      for person in day['data']]})

    with open('clean_data.json', 'w') as outfile:
        json.dump(clean_days, outfile)


PG = ['getBasicInfOfPG', 'getPercentOFAttendedSessionPG', 'getMPsOfPG',
      'getMostMatchingThem', 'getLessMatchingThem', 'getDeviationInOrg',
      'getTaggedBallots', 'getVocabularySize', 'getStyleScores',
      'getTFIDF', 'getNumberOfQuestions', 'getQuestionsOfPG',
      'getPresenceThroughTime', 'getIntraDisunionOrg', 'getListOfPGs']
P = ['getMPStatic', 'getMostEqualVoters', 'getLeastEqualVoters', 'getTFIDF',
     'getPresence', 'getStyleScores', 'getAverageNumberOfSpeechesPerSession',
     'getNumberOfSpokenWords', 'getLastActivity', 'getVocabularySize',
     'getVocabularySizeLanding', 'getUniqueWordsLanding', 'getAllSpeeches',
     'getQuestions', 'getPresenceThroughTime', 'getListOfMembersTickers',
     'getCompass', 'getTaggedBallots', 'getMembershipsOfMember',
     'getNumberOfQuestions', 'getListOfMembers']
S = ['getSpeechesOfSession', 'getSpeechesIDsOfSession', 'getPresenceOfPG',
     'getTFIDF', 'getMotionOfSession']
SV = ['getMotionGraph', 'getMotionAnalize']


def measureApiTimes():
    times = {}

    times['vote'] = tajmer('https://analize.parlameter.si/v1/s/',
                           SV,
                           6900)
    print 'end SV'
    times['person'] = tajmer('https://analize.parlameter.si/v1/p/',
                             P,
                             11)
    print 'end P'
    times['org'] = tajmer('https://analize.parlameter.si/v1/pg/',
                          PG,
                          5)
    print 'end PG'
    times['session'] = tajmer('https://analize.parlameter.si/v1/s/',
                              S,
                              5583)


def tajmer(base_url, endpoints, id_):
    data = []
    for endpoint in endpoints:
        start = time.time()
        resp = requests.get(base_url + endpoint + '/' + str(id_))
        end = time.time()
        data.append({'endpoint': endpoint,
                     'time': (end - start),
                     'status': resp.status_code})
    return data
