# -*- coding: utf-8 -*-
import requests

from parlalize.settings import API_URL, API_DATE_FORMAT, BASE_URL, GLEJ_URL, slack_token, SETTER_KEY, DZ
from parlalize.utils_ import getPGIDs, findDatesFromLastCard
from datetime import datetime, timedelta
from django.apps import apps
from raven.contrib.django.raven_compat.models import client
from django.test.client import RequestFactory
from itertools import groupby

from parlaposlanci.views import setMembershipsOfMember, setLastActivity, setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords, setListOfMembersTickers, setPresenceThroughTime, setNumberOfQuestionsAll, setPercentOFAttendedSession
from parlaposlanci.models import Person, MPStaticPL, MembershipsOfMember, AverageNumberOfSpeechesPerSession, MinisterStatic

from parlaskupine.views import setWorkingBodies, getListOfPGs
from parlaskupine.models import Organization, WorkingBodies, MPOfPg, PGStatic, PGMismatch

from parlaseje.models import Legislation, Session, Vote, Ballot, Speech, Question, Tag, AbsentMPs, Vote_analysis

from parlaseje.views import getSessionsList, setMotionOfSession
from parlaseje.utils_ import idsOfSession, getSesDates, speech_the_order
from utils.votes_outliers import setMotionAnalize, setOutliers
from utils.votes_pg import set_mismatch_of_pg

from .votes import VotesAnalysis
from .delete_renders import deleteMPandPGsRenders, deleteRendersOfSession, deleteRendersOfIDs, delete_renders, refetch

from parlalize.utils_ import tryHard, datesGenerator, printProgressBar, getPersonData, getAllStaticData

import json
from slackclient import SlackClient

from time import time

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)


# parlaposlanci runner methods #


def onDateMPCardRunner(date_=None):
    """
    Create all cards for data_ date. If date_ is None set for run setters
    for today.
    """
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        dateObj = datetime.strptime(date_, API_DATE_FORMAT)
        date_of = (dateObj - timedelta(days=1)).date()
    else:
        date_of = (datetime.now() - timedelta(days=1)).date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    votez = VotesAnalysis(date_of)
    votez.setAll()
    set_mismatch_of_pg(None, date_)
    setters = [
        setMembershipsOfMember,
        setPresenceThroughTime,
        setPercentOFAttendedSession,
    ]

    memberships = tryHard(API_URL + '/getMPs/' + date_).json()

    for membership in memberships:
        print(membership['id'])
        for setter in setters:
            print 'running:' + str(setter)
            try:
                setter(request_with_key, str(membership['id']), date_)
            except:
                msg = ('' + FAIL + ''
                       'FAIL on: '
                       '' + str(setter) + ''
                       ' and with id: '
                       '' + str(membership['id']) + ''
                       '' + ENDC + '')
                print msg

    # Runner for setters ALL
    all_in_one_setters = [
        setAverageNumberOfSpeechesPerSessionAll,
        setNumberOfQuestionsAll,
        setVocabularySizeAndSpokenWords,
    ]

    zero = datetime(day=2, month=8, year=2014).date()
    for setter in all_in_one_setters:
        print 'running:' + str(setter)
        try:
            setter(request_with_key, date_)
        except:
            print 'FAIL on: ' + str(setter)

"""
    When are membersips changed, run this method for update data and page
"""
def onMembershipChangePGRunner(data, date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        dateObj = datetime.strptime(date_, API_DATE_FORMAT)
        date_of = dateObj.date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    pg_ids = data['pgs']
    mp_ids = data['mps']

    votez = VotesAnalysis(date_of)
    votez.setAll()
    set_mismatch_of_pg(None)

    setters_mp = [
        setMembershipsOfMember,
    ]

    for mp in mp_ids:
        for setter in setters_mp:
            try:
                setter(request_with_key, str(mp), date_)
            except:
                msg = ('' + FAIL + ''
                       'FAIL on: '
                       '' + str(setter) + ''
                       ' and with id: '
                       '' + str(membership['id']) + ''
                       '' + ENDC + '')
                print msg

    pg_setters = [
    ]
    for setter in pg_setters:
        for pg_id in pg_ids:
            try:
                setter(request_with_key, str(pg_id), date_)
            except:
                text = ('' + FAIL + 'FAIL on: ' + str(setter) + ''
                        ' and with id: ' + str(pg_id) + ENDC + '')
                print text

    getAllStaticData(None, force_render=True)
    getListOfPGs(None, date_, force_render=True)
    deleteMPandPGsRenders()



def onDatePGCardRunner(date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        dateObj = datetime.strptime(date_, API_DATE_FORMAT)
        date_of = (dateObj - timedelta(days=1)).date()
    else:
        date_of = (datetime.now() - timedelta(days=1)).date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    print date_
    set_mismatch_of_pg(None)
    votez = VotesAnalysis(date_of) # TODO
    votez.setAll()
    setters = [
    ]

    membersOfPGsRanges = tryHard(
        API_URL + '/getMembersOfPGsRanges/' + date_).json()
    IDs = [key for key, value in membersOfPGsRanges[-1]['members'].items()
           if value]
    curentId = 0

    for setter in setters:
        for ID in IDs:
            print setter
            try:
                setter(request_with_key, str(ID), date_)
            except:
                text = ('' + FAIL + 'FAIL on: ' + str(setter) + ''
                        ' and with id: ' + str(ID) + ENDC + '')
                print text

    # Runner for setters ALL
    all_in_one_setters = [
    ]

    for setter in all_in_one_setters:
        try:
            setter(request_with_key, date_)
        except:
            print FAIL + 'FAIL on: ' + str(setter) + ENDC

    # updateWB()


def runSettersSessions(date_to=None, sessions_ids=None):
    if not date_to:
        date_to = datetime.today().strftime(API_DATE_FORMAT)

    setters_models = {
        Vote_analysis: setMotionAnalize,
    }
    # set outliers for all votes
    # TODO remove next comment when algoritem for is_outlier will be fixed
    #setOutliers()
    for model, setter in setters_models.items():
        # IDs = getSesIDs(dates[1],dates[-1])
        if sessions_ids:
            last = sessions_ids
        else:
            last = idsOfSession(model)
        print last
        print model
        for ID in last:
            print ID
            try:
                setter(request_with_key, str(ID))
            except:
                client.captureException()
    return 'all is fine :D'


def updateLastDay(date_=None):
    if not date_:
        to_date = datetime.now()
    else:
        to_date = date_

    votes = Vote.objects.filter(start_time__lte=to_date)
    lastVoteDay = votes.latest('created_for').created_for
    speeches = Speech.objects.filter(start_time__lte=to_date)
    lastSpeechDay = speeches.latest('start_time').start_time

    votez = VotesAnalysis(to_date)
    votez.setAll()

    runForTwoDays = True

    if lastVoteDay == lastSpeechDay.date():
        runForTwoDays = False

    try:
        onDateMPCardRunner(lastVoteDay.strftime(API_DATE_FORMAT))
    except:
        client.captureException()
    try:
        onDatePGCardRunner(lastVoteDay.strftime(API_DATE_FORMAT))
    except:
        client.captureException()

    # if last vote and speech isn't in the same day
    if runForTwoDays:
        try:
            onDateMPCardRunner(lastSpeechDay.strftime(API_DATE_FORMAT))
        except:
            client.captureException()
        try:
            onDatePGCardRunner(lastSpeechDay.strftime(API_DATE_FORMAT))
        except:
            client.captureException()

    return 1


def deleteAppModels(appName):
    my_app = apps.get_app_config(appName)
    my_models = my_app.get_models()
    for model in my_models:
        print 'delete model: ', model
        model.objects.all().delete()


def updateWB():
    organizations = tryHard(API_URL + '/getOrganizatonsByClassification').json()
    for wb in organizations['working_bodies'] + organizations['council']:
        print 'setting working_bodie: ', wb['name']
        try:
            setWorkingBodies(request_with_key,
                             str(wb['id']),
                             datetime.now().date().strftime(API_DATE_FORMAT))
            requests.get(GLEJ_URL + '/wb/getWorkingBodies/' + str(wb['id']) + '?frame=true&altHeader=true&forceRender=true')
            requests.get(GLEJ_URL + '/wb/getWorkingBodies/' + str(wb['id']) + '?embed=true&altHeader=true&forceRender=true')
            requests.get(GLEJ_URL + '/wb/getWorkingBodies/' + str(wb['id']) + '?altHeader=true&forceRender=true')
        except:
            client.captureException()

    return 'all is fine :D WB so settani'


def setListOfMembers(date_time):
    """
    TODO: naredi da se posle mejl ko se doda nova redna seja.
    Ker je potrebno pognat se style score na searchu.
    """
    start_date = datetime.strptime(date_time, '%Y-%m-%dT%X')
    start_date = start_date - timedelta(days=1)
    setListOfMembersTickers(request_with_key, start_date.strftime(API_DATE_FORMAT))
