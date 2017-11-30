# -*- coding: utf-8 -*-
import requests
from parlaposlanci.views import setMPStaticPL
from parlalize.settings import API_URL, API_DATE_FORMAT, BASE_URL, GLEJ_URL, slack_token, SETTER_KEY
from parlalize.utils_ import getPGIDs, findDatesFromLastCard
from datetime import datetime, timedelta
from django.apps import apps
from raven.contrib.django.raven_compat.models import client
from django.test.client import RequestFactory
from itertools import groupby

from parlaposlanci.views import setMPStaticPL, setMembershipsOfMember, setLastActivity, setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords, setCompass, setListOfMembersTickers, setPresenceThroughTime, setMinsterStatic, setNumberOfQuestionsAll, setPercentOFAttendedSession
from parlaposlanci.models import Person, MPStaticPL, MembershipsOfMember, AverageNumberOfSpeechesPerSession, Compass, MinisterStatic

from parlaskupine.views import setMPsOfPG, setBasicInfOfPG, setWorkingBodies, setVocabularySizeALL, getListOfPGs, setPresenceThroughTime as setPresenceThroughTimePG, setPGMismatch
from parlaskupine.models import Organization, WorkingBodies, MPOfPg, PGStatic, PGMismatch

from parlaseje.models import Legislation, Session, Vote, Ballot, Speech, Question, Tag, PresenceOfPG, AbsentMPs, VoteDetailed, Vote_analysis

from parlaseje.views import setPresenceOfPG, setMotionOfSessionGraph, getSessionsList, setMotionOfSession
from parlaseje.utils import idsOfSession, getSesDates
from utils.recache import updatePagesS, updateLastActivity, recacheActivities, recacheWBs
from utils.imports import update, updateDistricts, updateTags, updatePersonStatus
from utils.votes_outliers import setMotionAnalize, setOutliers
from utils.votes_pg import set_mismatch_of_pg
from utils.exports import exportLegislations

from .votes import VotesAnalysis

from parlalize.utils_ import tryHard, datesGenerator, printProgressBar, getPersonData

import json
from slackclient import SlackClient

from time import time

DZ = 95
factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)


# parlaposlanci runner methods #


def updateMPStatic():
    memberships = tryHard(API_URL + '/getMembersOfPGsRanges/').json()
    lastObject = {'members': {}}
    print '[info] update MP static'
    for change in memberships:
        # call setters for new pg
        for pg in list(set(change['members'].keys()) - set(lastObject['members'].keys())):
            for member in change['members'][pg]:
                setMPStaticPL(request_with_key, str(member), change['start_date'])

        # call setters for members which have change in memberships
        for pg in change['members'].keys():
            if pg in lastObject['members'].keys():
                personsForUpdate = list(set(change['members'][pg]) - set(lastObject['members'][pg]))
                for member in personsForUpdate:
                    setMPStaticPL(request_with_key, str(member), change['start_date'])
        lastObject = change


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
        setCompass,
    ]

    zero = datetime(day=2, month=8, year=2014).date()
    for setter in all_in_one_setters:
        print 'running:' + str(setter)
        try:
            setter(request_with_key, date_)
        except:
            print 'FAIL on: ' + str(setter)


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
    setters = [
        setMPsOfPG,
        setBasicInfOfPG,
        setPresenceThroughTimePG,
        setPGMismatch,
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
        setVocabularySizeALL,
    ]

    for setter in all_in_one_setters:
        try:
            setter(request_with_key, date_)
        except:
            print FAIL + 'FAIL on: ' + str(setter) + ENDC

    set_mismatch_of_pg()

    # updateWB()


def runSettersSessions(date_to=None, sessions_ids=None):
    if not date_to:
        date_to = datetime.today().strftime(API_DATE_FORMAT)

    setters_models = {
        PresenceOfPG: setPresenceOfPG,
        VoteDetailed: setMotionOfSessionGraph,
        Vote_analysis: setMotionAnalize,
    }
    # set outliers for all votes
    setOutliers()
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


def updateAll():
    update()

    print 'mp static'
    updateMPStatic()

    print 'start update cards'
    updateLastDay()

    return 1


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


def fastUpdate(fast=True, date_=None):
    sc = SlackClient(slack_token)
    start_time = time()
    yesterday = (datetime.now()-timedelta(days=1)).date()
    yesterday = datetime.combine(yesterday, datetime.min.time())
    new_redna_seja = []
    lockFile = open('parser.lock', 'w+')
    lockFile.write('LOCKED')
    lockFile.close()
    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text='Start fast update at: ' + str(datetime.now()))

    dates = []

    lastBallotTime = Ballot.objects.latest('updated_at').updated_at
    lastVoteTime = Vote.objects.latest('updated_at').updated_at
    lastSpeechTime = Speech.objects.latest('updated_at').updated_at
    lastQustionTime = Question.objects.latest('updated_at').updated_at
    #lastLegislationTime = Legislation.objects.latest('updated_at').updated_at
    if date_:
        dates = [date_ + '_00:00' for i in range(5)]
    else:
        # get dates of last update
        dates.append(Person.objects.latest('updated_at').updated_at)
        dates.append(Session.objects.latest('updated_at').updated_at)
        dates.append(lastSpeechTime)
        dates.append(lastBallotTime)
        dates.append(Question.objects.latest('updated_at').updated_at)
        
        lastLegislationTime=datetime.now()-timedelta(days=10)
        dates.append(lastLegislationTime)

    # prepare url
    url = API_URL + '/getAllChangesAfter/'
    for sDate in dates:
        url += sDate.strftime(API_DATE_FORMAT + '_%H:%M') + '/'

    print url

    data = tryHard(url[:-1]).json()

    print 'Speeches: ', len(data['speeches'])
    print 'Sessions: ', len(data['sessions'])
    print 'Persons: ', len(data['persons'])
    print 'Questions: ', len(data['questions'])
    print 'Legislation: ', len(data['laws'])

    text = ('Received data: \n'
            'Speeches: ' + str(len(data['speeches'])) + '\n'
            'Sessions: ' + str(len(data['sessions'])) + '\n'
            'Persons: ' + str(len(data['persons'])) + '\n'
            'Questions: ' + str(len(data['questions'])) + '\n'
            'Legislation: ' + str(len(data['laws'])) + '\n'
            )
    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text=text)

    sdate = datetime.now().strftime(API_DATE_FORMAT)

    # Persons
    mps = tryHard(API_URL + '/getMPs/' + sdate).json()
    mps_ids = [mp['id'] for mp in mps]
    for mp in data['persons']:
        if Person.objects.filter(id_parladata=mp['id']):
            person = Person.objects.get(id_parladata=mp['id'])
            person.name = mp['name']
            person.pg = mp['membership']
            person.id_parladata = int(mp['id'])
            person.image = mp['image']
            person.actived = True if int(mp['id']) in mps_ids else False
            person.gov_id = mp['gov_id']
            person.save()
        else:
            actived = True if int(mp['id']) in mps_ids else False
            person = Person(name=mp['name'],
                            pg=mp['membership'],
                            id_parladata=int(mp['id']),
                            image=mp['image'],
                            actived=actived,
                            gov_id=mp['gov_id'])
            person.save()

    session_ids = list(Session.objects.all().values_list('id_parladata',
                                                         flat=True))

    # sessions
    for sessions in data['sessions']:
        orgs = Organization.objects.filter(id_parladata__in=sessions['organizations_id'])
        if not orgs:
            orgs = Organization.objects.filter(id_parladata=sessions['organization_id'])
        if sessions['id'] not in session_ids:
            result = Session(name=sessions['name'],
                             gov_id=sessions['gov_id'],
                             start_time=sessions['start_time'],
                             end_time=sessions['end_time'],
                             classification=sessions['classification'],
                             id_parladata=sessions['id'],
                             organization=orgs[0],
                             in_review=sessions['is_in_review']
                             )
            result.save()
            orgs = list(orgs)
            result.organizations.add(*orgs)
            if sessions['id'] == DZ:
                if 'redna seja' in sessions['name'].lower():
                    # call method for create new list of members
                    #new_redna_seja.append(sessions)
                    pass
        else:
            if not Session.objects.filter(name=sessions['name'],
                                          gov_id=sessions['gov_id'],
                                          start_time=sessions['start_time'],
                                          end_time=sessions['end_time'],
                                          classification=sessions['classification'],
                                          id_parladata=sessions['id'],
                                          organization=orgs[0],
                                          in_review=sessions['is_in_review']):
                # save changes
                session = Session.objects.get(id_parladata=sessions['id'])
                session.name = sessions['name']
                session.gov_id = sessions['gov_id']
                session.start_time = sessions['start_time']
                session.end_time = sessions['end_time']
                session.classification = sessions['classification']
                session.in_review = sessions['is_in_review']
                session.save()
                orgs = list(orgs)
                session.organizations.add(*orgs)

    # update Legislation
    for epa, laws in groupby(data['laws'], lambda item: item['epa']):
        last_obj = None
        sessions = []
        is_ended = False
        for law in laws:
            sessions.append(law['session'])
            law['date'] = datetime.strptime(law['date'], '%Y-%m-%dT%X')
            if not is_ended:
                if law['procedure_ended']:
                    is_ended = True
            if last_obj:
                if law['date'] > last_obj['date']:
                    last_obj = law
            else: 
                last_obj = law
        result = Legislation.objects.filter(epa=epa)

        # dont update Legislatin procedure_ended back to False
        if result:
            result = result[0]
            if result.procedure_ended:
                is_ended = True
            print 'update'
            result.text = last_obj['text']
            result.mdt = last_obj['mdt']
            result.proposer_text = last_obj['proposer_text']
            result.procedure_phase = last_obj['procedure_phase']
            result.procedure = last_obj['procedure']
            result.type_of_law = last_obj['type_of_law']
            result.id_parladata = last_obj['id']
            result.date = last_obj['date']
            result.procedure_ended = is_ended
            result.classification = last_obj['classification']
            result.save()
        else:
            print 'adding'
            result = Legislation(text=last_obj['text'],
                                 epa=last_obj['epa'],
                                 mdt=last_obj['mdt'],
                                 proposer_text=last_obj['proposer_text'],
                                 procedure_phase=last_obj['procedure_phase'],
                                 procedure=last_obj['procedure'],
                                 type_of_law=last_obj['type_of_law'],
                                 id_parladata=last_obj['id'],
                                 date=last_obj['date'],
                                 procedure_ended=is_ended,
                                 classification=['classification'],
                                 )
            result.save()
        sessions = list(set(sessions))
        sessions = list(Session.objects.filter(id_parladata__in=sessions))
        result.sessions.add(*sessions)
        print(epa)
    if data['laws']:
        print 'legislation'
        exportLegislations()

    # update speeches
    existingIDs = list(Speech.objects.all().values_list('id_parladata',
                                                        flat=True))
    sc.api_call('chat.postMessage',
                channel='#parlalize_notif',
                text='Start update speeches at: ' + str(datetime.now()))
    for dic in data['speeches']:
        if int(dic['id']) not in existingIDs:
            print 'adding speech'
            person = Person.objects.get(id_parladata=int(dic['speaker']))
            speech = Speech(person=person,
                            organization=Organization.objects.get(
                                id_parladata=int(dic['party'])),
                            content=dic['content'], order=dic['order'],
                            session=Session.objects.get(
                                id_parladata=int(dic['session'])),
                            start_time=dic['start_time'],
                            end_time=dic['end_time'],
                            valid_from=dic['valid_from'],
                            valid_to=dic['valid_to'],
                            id_parladata=dic['id'])
            speech.save()
        else:
            print "update speech"
            person = Person.objects.get(id_parladata=int(dic['speaker']))
            speech = Speech.objects.filter(id_parladata=dic["id"])
            speech.update(content=dic['content'],
                          person=person,
                          valid_from=dic['valid_from'],
                          valid_to=dic['valid_to'])

    # update Votes
    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text='Start update votes at: ' + str(datetime.now()))
    for session_id in data['sessions_of_updated_votes']:
        setMotionOfSession(request_with_key, str(session_id))

    # update ballots
    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text='Start update ballots at: ' + str(datetime.now()))
    existingISs = Ballot.objects.all().values_list('id_parladata', flat=True)
    for dic in data['ballots']:
        if int(dic['id']) not in existingISs:
            print 'adding ballot ' + str(dic['vote'])
            vote = Vote.objects.get(id_parladata=dic['vote'])
            person = Person.objects.get(id_parladata=int(dic['voter']))
            ballots = Ballot(person=person,
                             option=dic['option'],
                             vote=vote,
                             start_time=vote.start_time,
                             end_time=None,
                             id_parladata=dic['id'])
            ballots.save()

    # update questions
    existingISs = list(Question.objects.all().values_list('id_parladata',
                                                          flat=True))
    for dic in data['questions']:
        if int(dic['id']) not in existingISs:
            print 'adding question'
            if dic['session_id']:
                session = Session.objects.get(id_parladata=int(dic['session_id']))
            else:
                session = None
            link = dic['link'] if dic['link'] else None
            person = Person.objects.get(id_parladata=int(dic['author_id']))
            if dic['recipient_id']:
                rec_p = list(Person.objects.filter(id_parladata__in=dic['recipient_id']))
            else:
                rec_p = []
            if dic['recipient_org_id']:
                rec_org = list(Organization.objects.filter(id_parladata__in=dic['recipient_org_id']))
            else:
                rec_org = []
            if dic['author_org_id']:
                author_org = Organization.objects.get(id_parladata=dic['author_org_id'])
            else:
                author_org = None
            rec_posts = []
            for post in dic['recipient_posts']:
                static = MinisterStatic.objects.filter(person__id_parladata=post['membership__person_id'],
                                                       ministry__id_parladata=post['organization_id']).order_by('-created_for')
                if static:
                    rec_posts.append(static[0])
            question = Question(person=person,
                                session=session,
                                start_time=dic['date'],
                                id_parladata=dic['id'],
                                recipient_text=dic['recipient_text'],
                                title=dic['title'],
                                content_link=link,
                                author_org=author_org,
                                )
            question.save()
            question.recipient_persons.add(*rec_p)
            question.recipient_organizations.add(*rec_org)
            question.recipient_persons_static.add(*rec_posts)

    updateDistricts()

    updateTags()

    if data['persons']:
        print 'mp static'
        updateMPStatic()
        print 'update person status'
        updatePersonStatus()

    t_delta = time() - start_time

    text = ('End fast update (' + str(t_delta) + ' s) and start'
            'update sessions cards at: ' + str(datetime.now()) + '')

    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text=text)

    print 'sessions'
    s_update = []
    # sessions = Session.objects.filter(updated_at__gte=datetime.now().date)
    # s_update += list(sessions.values_list('id_parladata', flat=True))
    votes = Vote.objects.filter(updated_at__gt=lastVoteTime)
    s_update += list(votes.values_list('session__id_parladata', flat=True))
    ballots = Ballot.objects.filter(updated_at__gt=lastBallotTime)
    s_update += list(ballots.values_list('vote__session__id_parladata',
                                         flat=True))

    p_update = list(ballots.values_list("person__id_parladata", flat=True))

    if s_update:
        runSettersSessions(sessions_ids=list(set(s_update)))

    t_delta = time() - start_time

    text = ('End creating cards (' + str(t_delta) + ' s) and start'
            'creating recache: ' + str(datetime.now()) + '')
    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text=text)

    lockFile = open('parser.lock', 'w+')
    lockFile.write('UNLOCKED')
    lockFile.close()

    # recache

    # add sesessions of updated speeches to recache
    if fast:
        speeches = Speech.objects.filter(updated_at__gt=lastSpeechTime)
    else:
        speeches = Speech.objects.filter(updated_at__gt=yesterday)
    s_update += list(speeches.values_list("session__id_parladata", flat=True))
    s_p_update = list(speeches.values_list("person__id_parladata", flat=True))

    date_ = (datetime.now() + timedelta(days=1)).strftime(API_DATE_FORMAT)
    if s_update:
        getSessionsList(None, date_, force_render=True)
    print s_update
    if s_update:
        print 'recache'
        updatePagesS(list(set(s_update)))
        requests.get('https://parlameter.si/fetch/sps?t=vkSzv8Nu4eDkLBk7kUw4BBhyLjysJm')
        if not fast:
            updateWB()

    p_update += list(speeches.values_list("person__id_parladata", flat=True))

    if fast:
        questions = Question.objects.filter(updated_at__gt=lastQustionTime)
    else:
        questions = Question.objects.filter(updated_at__gt=yesterday)
    q_update = list(questions.values_list("person__id_parladata", flat=True))
    p_update += q_update

    # if "fast" fastUpdate then skip update last activites
    if not fast:
        updateLastActivity(list(set(p_update)))
        recacheActivities(('poslanska-vprasanja-in-pobude',
                           'poslanska-vprasanja-in-pobude'),
                          list(set(q_update)))
        recacheActivities(('povezave-do-govorov',
                           'vsi-govori-poslanske-skupine'),
                          list(set(s_p_update)))
        recacheWBs()

    t_delta = time() - start_time

    text = ('End fastUpdate everything (' + str(t_delta) + ' s): '
            '' + str(datetime.now()) + '')

    sc.api_call("chat.postMessage",
                channel="#parlalize_notif",
                text=text)

    for session in new_redna_seja:
        # run cards
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='New redna seja: ' + session.name + ' Start creating cards')

        updateLastDay(session.date)
        setListOfMembers(sessions['start_time'])
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='New P and PG cards was created.')


def setListOfMembers(date_time):
    """
    TODO: naredi da se posle mejl ko se doda nova redna seja.
    Ker je potrebno pognat se style score na searchu.
    """
    start_date = datetime.strptime(date_time, '%Y-%m-%dT%X')
    start_date = start_date - timedelta(days=1)
    setListOfMembersTickers(request_with_key, start_time.strftime(API_DATE_FORMAT))


