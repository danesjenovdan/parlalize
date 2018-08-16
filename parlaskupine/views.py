# -*- coding: UTF-8 -*-
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models.functions import Trunc

from collections import Counter
from scipy.stats.stats import pearsonr
from scipy.spatial.distance import euclidean
from itertools import groupby
from datetime import timedelta, datetime

import requests
import json
import math
import numpy as np

from utils.speech import WordAnalysis
from parlalize.utils_ import (tryHard, lockSetter, prepareTaggedBallots, findDatesFromLastCard,
                              getAllStaticData, setCardData, getPersonCardModelNew,
                              getPGCardModelNew, getPersonData, saveOrAbortNew, getDataFromPagerApi)
from parlalize.settings import (API_URL, API_DATE_FORMAT, BASE_URL,
                                API_OUT_DATE_FORMAT, SETTER_KEY, VOTE_NAMES, YES, NOT_PRESENT,
                                AGAINST, ABSTAIN)
from .models import *
from .utils_ import getDisunionInOrgHelper, getAmendmentsCount
from parlaseje.models import Activity, Session, Vote, Speech, Question
from parlaposlanci.models import Person, MismatchOfPG
from parlaposlanci.views import getMPsList
from kvalifikatorji.scripts import (countWords, getCountListPG, getScores,
                                    problematicno, privzdignjeno, preprosto)


@lockSetter
def setBasicInfOfPG(request, pg_id, date_=None):
    """Set method for basic information for PGs.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        url = API_URL + '/getBasicInfOfPG/' + str(pg_id) + '/' + date_
        data = tryHard(url).json()
    else:
        date_of = datetime.now().date()
        url = API_URL+'/getBasicInfOfPG/' + str(pg_id) + '/'
        data = tryHard(url).json()

    headOfPG = 0
    viceOfPG = []
    if data['HeadOfPG'] is not None:
        headOfPG = Person.objects.get(id_parladata=int(data['HeadOfPG']))
    else:
        headOfPG = None

    if data['ViceOfPG']:
        for vice in data['ViceOfPG']:
            if vice is not None:
                viceOfPG.append(vice)
            else:
                viceOfPG.append(None)
    else:
                viceOfPG.append(None)
    org = Organization.objects.get(id_parladata=int(pg_id))
    result = saveOrAbortNew(model=PGStatic,
                            created_for=date_of,
                            organization=org,
                            headOfPG=headOfPG,
                            viceOfPG=viceOfPG,
                            numberOfSeats=data['NumberOfSeats'],
                            allVoters=data['AllVoters'],
                            facebook=data['Facebook'],
                            twitter=data['Twitter'],
                            email=data['Mail']
                            )

    return JsonResponse({'alliswell': True})


def getBasicInfOfPG(request, pg_id, date=None):
    """
    * @api {get} getBasicInfOfPG/{pg_id} Get basic info of a PG
    * @apiName getBasicInfOfPG
    * @apiGroup PGs
    * @apiDescription This function returns basic data of a selected PG
    * @apiParam {Integer} pg_id Parladata id for the PG in question.

    * @apiSuccess {Integer} allVoters [WRONG] Calculated number of voters who voted for this PG. This number is not reliable, do not use it.
    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} headOfPg The president of the PG
    * @apiSuccess {Boolean} headOfPg.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} headOfPg.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} headOfPg.name MP's full name.
    * @apiSuccess {String} headOfPg.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} headOfPg.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} headOfPg.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} headOfPg.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} headOfPg.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} headOfPg.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} headOfPg.party.name The party's name.
    * @apiSuccess {String} headOfPg.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} headOfPg.id The person's Parladata id.
    * @apiSuccess {Boolean} headOfPg.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {Object} social Social media links for this PG
    * @apiSuccess {String} social.twitter Url to PG's Twitter account (or null)
    * @apiSuccess {String} social.facebook Url to PG's Facebook account (or null)
    * @apiSuccess {String} social.email The email address of the primary contact for this PG

    * @apiSuccess {Integer} numberOfSeats The number of seats this PG holds in the parliament.
    
    * @apiSuccess {Object} party The party object
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} viceOfPg List of objects representing PG's vice presidents.
    * @apiSuccess {Boolean} viceOfPg.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} viceOfPg.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} viceOfPg.name MP's full name.
    * @apiSuccess {String} viceOfPg.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} viceOfPg.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} viceOfPg.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} viceOfPg.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} viceOfPg.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} viceOfPg.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} viceOfPg.party.name The party's name.
    * @apiSuccess {String} viceOfPg.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} viceOfPg.id The person's Parladata id.
    * @apiSuccess {Boolean} viceOfPg.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getBasicInfOfPG/1

    * @apiSuccessExample {json} Example response:
    {
        "allVoters": 119061,
        "created_for": "13.02.2017",
        "headOfPG": {
            "is_active": false,
            "district": [102],
            "name": "Simona Kustec Lipicer",
            "gov_id": "P266",
            "gender": "f",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 48,
            "has_function": false
        },
        "social": {
            "twitter": "https://twitter.com/strankasmc",
            "facebook": "https://www.facebook.com/StrankaSMC/",
            "email": "monika.mandic@dz-rs.si"
        },
        "numberOfSeats": 35,
        "party": {
            "acronym": "SMC",
            "is_coalition": true,
            "id": 1,
            "name": "PS Stranka modernega centra"
        },
        "created_at": "28.02.2017",
        "viceOfPG": [{
            "is_active": false,
            "district": [30],
            "name": "Anita Kole\u0161a",
            "gov_id": "P260",
            "gender": "f",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 40,
            "has_function": false
        }, {
            "is_active": false,
            "district": [99],
            "name": "Du\u0161an Verbi\u010d",
            "gov_id": "P296",
            "gender": "m",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 92,
            "has_function": false
        }]
    }
    """
    card = getPGCardModelNew(PGStatic, pg_id, date)
    headOfPG = 0
    viceOfPG = []
    if card.headOfPG:
        headOfPG = getPersonData(card.headOfPG.id_parladata, date)
    else:
        headOfPG = 0
    for vice in card.viceOfPG:
        if vice:
            viceOfPG.append(getPersonData(vice, date))
        # else:
            # viceOfPG.append(0)

    data = {'party': card.organization.getOrganizationData(),
            'created_at': card.created_at.strftime(API_DATE_FORMAT),
            'created_for': card.created_for.strftime(API_DATE_FORMAT),
            'headOfPG': headOfPG,
            'viceOfPG': viceOfPG,
            'numberOfSeats': card.numberOfSeats,
            'allVoters': card.allVoters,
            'social': {
                'facebook': card.facebook,
                'twitter': card.twitter,
                'email': card.email
                }
            }

    return JsonResponse(data)


@lockSetter
def setPercentOFAttendedSessionPG(request, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = findDatesFromLastCard(PercentOFAttendedSession,
                                        pg_id,
                                        datetime.now().date())[0]

    allSum = {}
    data = {}

    membersOfPG = tryHard(API_URL+'/getMembersOfPGsOnDate/'+date_).json()
    data = tryHard(API_URL+'/getNumberOfAllMPAttendedSessions/'+date_).json()

    sessions = {pg: [] for pg in membersOfPG if membersOfPG[pg]}
    votes = {pg: [] for pg in membersOfPG if membersOfPG[pg]}
    for pg in membersOfPG:
        if not membersOfPG[pg]:
            continue
        for member in membersOfPG[pg]:
            if str(member) in data['sessions'].keys():
                sessions[pg].append(data['sessions'][str(member)])
                votes[pg].append(data['votes'][str(member)])
        sessions[pg] = sum(sessions[pg])/len(sessions[pg])
        votes[pg] = sum(votes[pg])/len(votes[pg])

    thisMPSessions = sessions[pg_id]
    maximumSessions = max(sessions.values())
    maximumPGSessions = [pgId
                         for pgId
                         in sessions
                         if sessions[pgId] == maximumSessions]
    averageSessions = sum(data['sessions'].values()) / len(data['sessions'])

    thisMPVotes = votes[pg_id]
    maximumVotes = max(votes.values())
    maximumPGVotes = [pgId
                      for pgId
                      in votes
                      if votes[pgId] == maximumVotes]
    averageVotes = sum(data['votes'].values()) / len(data['votes'])
    org = Organization.objects.get(id_parladata=int(pg_id))

    result = saveOrAbortNew(model=PercentOFAttendedSession,
                            created_for=date_of,
                            organization=org,
                            organization_value_sessions=thisMPSessions,
                            maxPG_sessions=maximumPGSessions,
                            average_sessions=averageSessions,
                            maximum_sessions=maximumSessions,
                            organization_value_votes=thisMPVotes,
                            maxPG_votes=maximumPGVotes,
                            average_votes=averageVotes,
                            maximum_votes=maximumVotes)

    return JsonResponse({'alliswell': True})


def getPercentOFAttendedSessionPG(request, pg_id, date_=None):
    """
    * @api {get} getPercentOFAttendedSessionPG/{pg_id}/{?date} Get percentage of attended sessions
    * @apiName getPercentOFAttendedSessionPG
    * @apiGroup PGs
    * @apiDescription This function returns the percentage of attended sessions and voting events for a specific PG.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created

    * @apiSuccess {Object} votes Presence at voting events
    * @apiSuccess {Object[]} votes.maxPG The The organization object.
    * @apiSuccess {String} votes.maxPG.acronym PG's acronym
    * @apiSuccess {Boolean} votes.maxPG.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} votes.maxPG.id PG's Parladata id.
    * @apiSuccess {String} votes.maxPG.name PG's name.
    * @apiSuccess {Float} votes.organization_value The percentage of attended voting events for the organization in question.
    * @apiSuccess {Float} votes.average The average percentage of attended voting events.
    * @apiSuccess {Float} votes.maximum The maximum percentage of attended voting events.

    * @apiSuccess {Object} sessions Presence at sessions
    * @apiSuccess {Object[]} sessions.maxPG The PG with the most attended sessions.
    * @apiSuccess {String} sessions.maxPG.acronym PG's acronym
    * @apiSuccess {Boolean} sessions.maxPG.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} sessions.maxPG.id PG's Parladata id.
    * @apiSuccess {String} sessions.maxPG.name PG's name.
    * @apiSuccess {Float} sessions.organization_value The percentage of attended sessions for the organization in question.
    * @apiSuccess {Float} sessions.average The average percentage of attended sessions.
    * @apiSuccess {Float} sessions.maximum The maximum percentage of attended sessions.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getPercentOFAttendedSessionPG/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getPercentOFAttendedSessionPG/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "organization": {
            "acronym": "SMC",
            "is_coalition": true,
            "id": 1,
            "name": "PS Stranka modernega centra"
        },
        "created_at": "17.05.2017",
        "created_for": "17.05.2017",
        "votes": {
            "maxPG": [{
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            }],
            "organization_value": 92.7485210066434,
            "average": 73.4046479186465,
            "maximum": 92.7485210066434
        },
        "sessions": {
            "maxPG": [{
                "acronym": "DeSUS",
                "is_coalition": true,
                "id": 3,
                "name": "PS Demokratska Stranka Upokojencev Slovenije"
            }],
            "organization_value": 93.5318406140705,
            "average": 84.0306159427153,
            "maximum": 93.5866013071896
        }
    }
    """
    card = getPGCardModelNew(PercentOFAttendedSession, pg_id, date_)
    max_s_orgs = [Organization.objects.get(id_parladata=pg).getOrganizationData()
                  for pg in card.maxPG_sessions]
    max_v_orgs = [Organization.objects.get(id_parladata=pg).getOrganizationData()
                  for pg in card.maxPG_votes]

    # uprasi ce isto kot pri personu razdelimo
    data = {'organization': card.organization.getOrganizationData(),
            'created_at': card.created_at.strftime(API_DATE_FORMAT),
            'created_for': card.created_for.strftime(API_DATE_FORMAT),
            'sessions': {
                'organization_value': card.organization_value_sessions,
                'maxPG': max_s_orgs,
                'average': card.average_sessions,
                'maximum': card.maximum_sessions,
                },
            'votes': {
                'organization_value': card.organization_value_votes,
                'maxPG': max_v_orgs,
                'average': card.average_votes,
                'maximum': card.maximum_votes,
                }
            }

    return JsonResponse(data)


@lockSetter
def setMPsOfPG(request, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = datetime.now().date()

    membersOfPG = tryHard(API_URL+'/getMembersOfPGsOnDate/' + date_).json()
    org = Organization.objects.get(id_parladata=pg_id)
    result = saveOrAbortNew(model=MPOfPg,
                            organization=org,
                            id_parladata=pg_id,
                            MPs=membersOfPG[pg_id],
                            created_for=date_of
                            )

    return JsonResponse({'alliswell': True})


def getMPsOfPG(request, pg_id, date_=None):
    """
    * @api {get} getPercentOFAttendedSessionPG/{pg_id}/{?date} Get percentage of attended sessions
    * @apiName getPercentOFAttendedSessionPG
    * @apiGroup PGs
    * @apiDescription This function returns the percentage of attended sessions and voting events for a specific PG.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created

    * @apiSuccess {Object} party The The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results List of MPs
    * @apiSuccess {Boolean} results.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.name MP's full name.
    * @apiSuccess {String} results.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.party.name The party's name.
    * @apiSuccess {String} results.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} results.id The person's Parladata id.
    * @apiSuccess {Boolean} results.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing). 

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getMPsOfPG/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getMPsOfPG/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "party": {
            "acronym": "IMNS",
            "is_coalition": false,
            "id": 2,
            "name": "PS italijanske in mad\u017earske narodne skupnosti"
        },
        "created_at": "28.02.2017",
        "created_for": "13.02.2017",
        "results": [{
            "is_active": false,
            "district": [91],
            "name": "L\u00e1szl\u00f3 G\u00f6ncz",
            "gov_id": "P117",
            "gender": "m",
            "party": {
                "acronym": "IMNS",
                "is_coalition": false,
                "id": 2,
                "name": "PS italijanske in mad\u017earske narodne skupnosti"
            },
            "type": "mp",
            "id": 24,
            "has_function": false
        }, {
            "is_active": false,
            "district": [90],
            "name": "Roberto Battelli",
            "gov_id": "P005",
            "gender": "m",
            "party": {
                "acronym": "IMNS",
                "is_coalition": false,
                "id": 2,
                "name": "PS italijanske in mad\u017earske narodne skupnosti"
            },
            "type": "mp",
            "id": 4,
            "has_function": false
        }]
    }
    """

    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = ''

    card = getPGCardModelNew(MPOfPg, pg_id, date_)
    ids = card.MPs
    result = sorted([getPersonData(MP, date_)
                     for MP in ids], key=lambda k: k['name'])
    created_at = card.created_at.strftime(API_DATE_FORMAT)
    created_for = card.created_for.strftime(API_DATE_FORMAT)
    return JsonResponse({'results': result,
                         'party': card.organization.getOrganizationData(),
                         'created_at': created_at,
                         'created_for': created_for})


def getSpeechesOfPG(request, pg_id, date_=False):
    """
    * @api {get} getSpeechesOfPG/{pg_id}/{?date} Get PG's speeches
    * @apiName getSpeechesOfPG
    * @apiGroup PGs
    * @apiDescription This function returns the list of last 21 days of speeches for a specific PG.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created

    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results List of Speeches
    * @apiSuccess {date} date The date in question
    * @apiSuccess {Object[]} sessions List of sessions on that day
    * @apiSuccess {String} sessions.session_name Name of the session
    * @apiSuccess {String} sessions.session_org The organization in which the session took place.
    
    * @apiSuccess {Object[]} sessions.speakers List of speakers from this PG who spoke at the session.

    * @apiSuccess {Object} sessions.speaker.person Person object for this speaker
    * @apiSuccess {Boolean} sessions.speaker.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} sessions.speaker.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} sessions.speaker.person.name MP's full name.
    * @apiSuccess {String} sessions.speaker.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} sessions.speaker.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} sessions.speaker.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} sessions.speaker.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} sessions.speaker.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} sessions.speaker.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} sessions.speaker.person.party.name The party's name.
    * @apiSuccess {String} sessions.speaker.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} sessions.speaker.person.id The person's Parladata id.
    * @apiSuccess {Boolean} sessions.speaker.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing). 
    
    * @apiSuccess {Integer} sessions.speeches List of speech ids for that speaker.

    * @apiSuccess {Integer} sessions.session_id Parladata id of the session in question

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getSpeechesOfPG/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getSpeechesOfPG/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {
        "party": {
            "acronym": "IMNS",
            "is_coalition": false,
            "id": 2,
            "name": "PS italijanske in mad\u017earske narodne skupnosti"
        },
        "created_at": "14.06.2017",
        "created_for": "14. 6. 2016",
        "results": [{
            "date": "10. 2. 2017",
            "sessions": [{
                "session_name": "87. redna seja",
                "session_org": "Kolegij predsednika dr\u017eavnega zbora",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [1110405]
                }],
                "session_id": 9155
            }]
        }, {
            "date": "2. 2. 2017",
            "sessions": [{
                "session_name": "33. redna seja",
                "session_org": "Odbor za finance in monetarno politiko",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [1158590, 1158570]
                }],
                "session_id": 8966
            }]
        }, {
            "date": "20. 12. 2016",
            "sessions": [{
                "session_name": "25. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [1248602, 1248590, 1248543]
                }],
                "session_id": 7654
            }]
        }, {
            "date": "15. 12. 2016",
            "sessions": [{
                "session_name": "25. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [1247957]
                }],
                "session_id": 7654
            }]
        }, {
            "date": "6. 12. 2016",
            "sessions": [{
                "session_name": "7. redna seja",
                "session_org": "Komisija za narodni skupnosti",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [1216615, 1216613, 1216611, 1216609, 1216607, 1216605, 1216604, 1216603, 1216602, 1216601, 1216600, 1216599, 1216598, 1216596, 1216594, 1216592, 1216588, 1216586, 1216585, 1216584, 1216583, 1216582, 1216580, 1216578, 1216577, 1216575, 1216572, 1216571, 1216569, 1216568, 1216566, 1216564, 1216562, 1216560, 1216558, 1216556, 1216554]
                }],
                "session_id": 8908
            }]
        }, {
            "date": "17. 11. 2016",
            "sessions": [{
                "session_name": "24. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [1256385, 1256379]
                }],
                "session_id": 5572
            }]
        }, {
            "date": "16. 11. 2016",
            "sessions": [{
                "session_name": "24. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [1256240]
                }],
                "session_id": 5572
            }]
        }, {
            "date": "12. 11. 2016",
            "sessions": [{
                "session_name": "68. nujna seja",
                "session_org": "Odbor za finance in monetarno politiko",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [633823]
                }],
                "session_id": 5970
            }]
        }, {
            "date": "3. 11. 2016",
            "sessions": [{
                "session_name": "22. redna seja",
                "session_org": "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [634797]
                }],
                "session_id": 6307
            }]
        }, {
            "date": "12. 10. 2016",
            "sessions": [{
                "session_name": "6. redna seja",
                "session_org": "Komisija za narodni skupnosti",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [595799, 595798, 595797, 595795, 595793, 595791, 595789, 595787, 595784, 595782, 595780, 595779, 595777, 595775, 595773, 595771, 595769, 595767, 595765, 595763, 595762, 595760, 595758, 595756]
                }],
                "session_id": 7425
            }, {
                "session_name": "7. nujna seja",
                "session_org": "Komisija za odnose s Slovenci v zamejstvu in po svetu",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [876273]
                }],
                "session_id": 7414
            }]
        }, {
            "date": "1. 10. 2016",
            "sessions": [{
                "session_name": "25. nujna seja",
                "session_org": "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [558096]
                }],
                "session_id": 6308
            }]
        }, {
            "date": "28. 9. 2016",
            "sessions": [{
                "session_name": "24. nujna seja",
                "session_org": "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [558345]
                }],
                "session_id": 6311
            }]
        }, {
            "date": "15. 7. 2016",
            "sessions": [{
                "session_name": "21. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [890570]
                }],
                "session_id": 5575
            }]
        }, {
            "date": "28. 6. 2016",
            "sessions": [{
                "session_name": "18. redna seja",
                "session_org": "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [91],
                        "name": "L\u00e1szl\u00f3 G\u00f6ncz",
                        "gov_id": "P117",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 24,
                        "has_function": false
                    },
                    "speeches": [558602]
                }],
                "session_id": 6315
            }]
        }, {
            "date": "14. 6. 2016",
            "sessions": [{
                "session_name": "20. redna seja",
                "session_org": "Dr\u017eavni zbor",
                "speakers": [{
                    "person": {
                        "is_active": false,
                        "district": [90],
                        "name": "Roberto Battelli",
                        "gov_id": "P005",
                        "gender": "m",
                        "party": {
                            "acronym": "IMNS",
                            "is_coalition": false,
                            "id": 2,
                            "name": "PS italijanske in mad\u017earske narodne skupnosti"
                        },
                        "type": "mp",
                        "id": 4,
                        "has_function": false
                    },
                    "speeches": [625866, 625828, 625815]
                }],
                "session_id": 5576
            }]
        }]
    }
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    speeches_q = Speech.getValidSpeeches(date_of + timedelta(days=1))
    staticData = json.loads(getAllStaticData(None).content)
    sessionsData = staticData['sessions']
    personsData = staticData['persons']
    out = []
    speeches = speeches_q.filter(organization__id_parladata=pg_id)

    speeches = speeches.annotate(day=Trunc("start_time",
                                          "day")).values('day',
                                                         'id_parladata',
                                                         'session__id_parladata',
                                                         'person__id_parladata',
                                                         'start_time',
                                                         'order')
    speeches = speeches.order_by('-day', 'session__id_parladata', 'person__id_parladata')

    out = []

    for day, group in groupby(speeches, lambda x: x['day']):
        day_objs = []
        for sessions_id, inner_group in groupby(group, lambda x: x['session__id_parladata']):
            thisSession = sessionsData[str(sessions_id)]
            session_obj = {'session_name': thisSession['name'],
                           'session_org': thisSession['org']['name'],
                           'session_id': thisSession['id'],
                           'speakers': []}
            #print list(inner_group)
            for person_id, inner_inner_group in groupby(inner_group, lambda x: x['person__id_parladata']):
                person_obj = {'person': personsData[str(person_id)].copy(),
                              'speeches': [s['id_parladata'] for s in inner_inner_group]}
                session_obj['speakers'].append(person_obj)
            #out[day][sessions_id][person_id] = [s['id_parladata'] for s in inner_inner_group]
            day_objs.append(session_obj)
        out.append({'date': day.strftime(API_OUT_DATE_FORMAT),
                    'sessions': day_objs})
        #print len(out)
        if len(out) > 50:
            break


    result = {
        'results': out,
        'created_for': out[-1]['date'],
        'created_at': date_,
        'party': Organization.objects.get(id_parladata=pg_id).getOrganizationData()
        }
    return JsonResponse(result, safe=False)


def getMostMatchingThem(request, pg_id, date_=None):
    """
    * @api {get} getMostMatchingThem/{pg_id}/{?date} Gets persons who can join specific organization
    * @apiName getMostMatchingThem
    * @apiGroup PGs
    * @apiDescription This function returns the list of 5 MPs who can join specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created

    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object[]} results.person List of MPs.
    * @apiSuccess {Boolean} results.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.person.name MP's full name.
    * @apiSuccess {String} results.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.person.party.name The party's name.
    * @apiSuccess {String} results.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} results.person.id The person's Parladata id.
    * @apiSuccess {Boolean} results.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.ratio Ratio of how the persoin can join the organization.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getLessMatchingThem/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getLessMatchingThem/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
   "organization":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"18.08.2017",
   "created_for":"14.07.2017",
   "results":[  
      {  
         "person":{  

         },
         "ratio":16.3235536544989
      },
      {  
         "person":{  

         },
         "ratio":18.674046697835
      },
      {  
         "person":{  
            "is_active":false,
            "district":[  
               19
            ],
            "name":"Franc Jurša",
            "gov_id":"P122",
            "gender":"m",
            "party":{  
               "acronym":"DeSUS",
               "is_coalition":true,
               "id":3,
               "name":"PS Demokratska Stranka Upokojencev Slovenije"
            },
            "type":"mp",
            "id":37,
            "has_function":false
         },
         "ratio":18.7601237281406
      },
      {  
         "person":{  

         },
         "ratio":18.9207916020778
      },
      {  
         "person":{  

         },
         "ratio":19.6466650769119
      }
   ]
}
    """
    mostMatching = getPGCardModelNew(MostMatchingThem, pg_id, date_)
    if not date_:
        date_ = ''
    org = Organization.objects.get(id_parladata=int(pg_id))
    out = {
        'organization': org.getOrganizationData(),
        'created_at': mostMatching.created_at.strftime(API_DATE_FORMAT),
        'created_for': mostMatching.created_for.strftime(API_DATE_FORMAT),
        'results': [
            {
                'ratio': mostMatching.votes1,
                'person': getPersonData(mostMatching.person1.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes2,
                'person': getPersonData(mostMatching.person2.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes3,
                'person': getPersonData(mostMatching.person3.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes4,
                'person': getPersonData(mostMatching.person4.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes5,
                'person': getPersonData(mostMatching.person5.id_parladata,
                                        date_)
            }
        ]
    }

    return JsonResponse(out, safe=False)


def getLessMatchingThem(request, pg_id, date_=None):
    """
    * @api {get} getLessMatchingThem/{pg_id}/{?date} Gets persons who can not join specific organization
    * @apiName getLessMatchingThem
    * @apiGroup PGs
    * @apiDescription This function returns the list of 5 MPs who can not join specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created

    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object[]} results.person List of MPs.
    * @apiSuccess {Boolean} results.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.person.name MP's full name.
    * @apiSuccess {String} results.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.person.party.name The party's name.
    * @apiSuccess {String} results.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} results.person.id The person's Parladata id.
    * @apiSuccess {Boolean} results.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.ratio Ratio of how the persoin can join the organization.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getLessMatchingThem/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getLessMatchingThem/1/12.12.2015

    * @apiSuccessExample {json} Example response:
  {
  "organization": {
    "acronym": "SMC",
    "is_coalition": true,
    "id": 1,
    "name": "PS Stranka modernega centra"
  },
  "created_at": "18.08.2017",
  "created_for": "14.07.2017",
  "results": [
    {
      "person": {
        "is_active": false,
        "district": [
          64
        ],
        "name": "Marko Pogačnik",
        "gov_id": "P196",
        "gender": "m",
        "party": {
          "acronym": "SDS",
          "is_coalition": false,
          "id": 5,
          "name": "PS Slovenska Demokratska Stranka"
        },
        "type": "mp",
        "id": 65,
        "has_function": false
      },
      "ratio": 64.7270144386353
    },
    {
      "person": {
        "is_active": false,
        "district": [
          70
        ],
        "name": "Jože Tanko",
        "gov_id": "P077",
        "gender": "m",
        "party": {
          "acronym": "SDS",
          "is_coalition": false,
          "id": 5,
          "name": "PS Slovenska Demokratska Stranka"
        },
        "type": "mp",
        "id": 78,
        "has_function": false
      },
      "ratio": 63.9854485386366
    },
    {
      "person": {
        "is_active": false,
        "district": [
          9
        ],
        "name": "Zvonko Lah",
        "gov_id": "P129",
        "gender": "m",
        "party": {
          "acronym": "NSI",
          "is_coalition": false,
          "id": 6,
          "name": "PS Nova Slovenija"
        },
        "type": "mp",
        "id": 49,
        "has_function": false
      },
      "ratio": 63.2064857978416
    },
    {
      "person": {
        "is_active": false,
        "district": [
          55
        ],
        "name": "Danijel Krivec",
        "gov_id": "P040",
        "gender": "m",
        "party": {
          "acronym": "SDS",
          "is_coalition": false,
          "id": 5,
          "name": "PS Slovenska Demokratska Stranka"
        },
        "type": "mp",
        "id": 47,
        "has_function": false
      },
      "ratio": 62.9069432744623
    },
    {
      "person": {
        "is_active": false,
        "district": [
          92
        ],
        "name": "Andrej Šircelj",
        "gov_id": "P201",
        "gender": "m",
        "party": {
          "acronym": "SDS",
          "is_coalition": false,
          "id": 5,
          "name": "PS Slovenska Demokratska Stranka"
        },
        "type": "mp",
        "id": 75,
        "has_function": false
      },
      "ratio": 62.2074947335552
    }
  ]
}
    """
    mostMatching = getPGCardModelNew(LessMatchingThem, pg_id, date_)
    if not date_:
        date_ = ''

    org = Organization.objects.get(id_parladata=int(pg_id))
    out = {
        'organization': org.getOrganizationData(),
        'created_at': mostMatching.created_at.strftime(API_DATE_FORMAT),
        'created_for': mostMatching.created_for.strftime(API_DATE_FORMAT),
        'results': [
            {
                'ratio': mostMatching.votes1,
                'person': getPersonData(mostMatching.person1.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes2,
                'person': getPersonData(mostMatching.person2.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes3,
                'person': getPersonData(mostMatching.person3.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes4,
                'person': getPersonData(mostMatching.person4.id_parladata,
                                        date_)
            },
            {
                'ratio': mostMatching.votes5,
                'person': getPersonData(mostMatching.person5.id_parladata,
                                        date_)
            }
        ]
    }
    return JsonResponse(out, safe=False)


def getDeviationInOrg(request, pg_id, date_=None):
    """
    * @api {get} getDeviationInOrg/{pg_id}/{?date} Gets persons who are most deviant from specific organization
    * @apiName getDeviationInOrg
    * @apiGroup PGs
    * @apiDescription This function returns the list of 35 MPs who are the most deviant specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object[]} results.person List of MPs.
    * @apiSuccess {Boolean} results.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.person.name MP's full name.
    * @apiSuccess {String} results.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.person.party.name The party's name.
    * @apiSuccess {String} results.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} results.person.id The person's Parladata id.
    * @apiSuccess {Boolean} results.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Object} results.person.party The organization object.
    * @apiSuccess {String} results.person.party.acronym PG's acronym
    * @apiSuccess {Boolean} results.person.party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} results.person.party.id PG's Parladata id.
    * @apiSuccess {String} results.person.party.name PG's name.
    * @apiSuccess {Float} results.ratio Ratio of how the persoin can join the organization.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getDeviationInOrg/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getDeviationInOrg/1/12.12.2015

    * @apiSuccessExample {json} Example response:
 {
  "organization": {
    "acronym": "SMC",
    "is_coalition": true,
    "id": 1,
    "name": "PS Stranka modernega centra"
  },
  "created_at": "18.08.2017",
  "created_for": "14.07.2017",
  "results": [
    {
      "person": {
        "name": "Vlasta Počkaj",
        "gov_id": "P303",
        "gender": "f",
        "is_active": false,
        "district": [
          84
        ],
        "party": {
          "acronym": "SMC",
          "is_coalition": true,
          "name": "PS Stranka modernega centra",
          "id": 1
        },
        "type": "mp",
        "id": 2934,
        "has_function": false
      },
      "ratio": 36.0512436698802
    },
    {
      "person": {
        "name": "Simon Zajc",
        "gov_id": "P293",
        "gender": "m",
        "is_active": false,
        "district": [
          100
        ],
        "party": {
          "acronym": "SMC",
          "is_coalition": true,
          "name": "PS Stranka modernega centra",
          "id": 1
        },
        "type": "mp",
        "id": 87,
        "has_function": false
      },
      "ratio": 8.320134474726908
    },
    {
      "person": {
        "name": "Urška Ban",
        "gov_id": "P240",
        "gender": "f",
        "is_active": false,
        "district": [
          8
        ],
        "party": {
          "acronym": "SMC",
          "is_coalition": true,
          "name": "PS Stranka modernega centra",
          "id": 1
        },
        "type": "mp",
        "id": 3,
        "has_function": false
      },
      "ratio": 7.1179380243116706
    }
  ]
}
    """
    mostMatching = getPGCardModelNew(DeviationInOrganization, pg_id, date_)
    if not date_:
        date_ = ''
    out_r = []
    for result in mostMatching.data:
        out_r.append({
            'ratio': result['ratio'],
            'person': getPersonData(int(result['id']), date_)})
    org = Organization.objects.get(id_parladata=int(pg_id))
    out = {
        'organization': org.getOrganizationData(),
        'created_at': mostMatching.created_at.strftime(API_DATE_FORMAT),
        'created_for': mostMatching.created_for.strftime(API_DATE_FORMAT),
        'results': out_r
    }
    # remove None from list. If PG dont have 6 members.
    out['results'] = filter(lambda a: a is not None, out['results'])
    return JsonResponse(out, safe=False)


def setWorkingBodies(request, org_id, date_=None):
    """The method for setting working bodies.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
    url = API_URL + '/getOrganizationRolesAndMembers/' + org_id + (('/'+date_) if date_ else '')
    members = tryHard(url).json()
    if not len(members['president']) or not len(members['members']) or not len(members['vice_president']):
        return JsonResponse({'alliswell': False,
                             'status': {'president_count': len(members['president']),
                                        'vice_president': len(members['vice_president']),
                                        'members': len(members['members']),
                                        'viceMember': len(members['viceMember'])
                                        }})
    out = {}
    name = members.pop('name')
    all_members = [member for role in members.values() for member in role]
    coalitionPGs = tryHard(API_URL+'/getCoalitionPGs/').json()
    membersOfPG = tryHard(API_URL+'/getMembersOfPGsOnDate/'+date_).json()
    sessions = tryHard(API_URL+'/getSessionsOfOrg/'+org_id+(('/'+date_) if date_ else '')).json()
    coal_pgs = {str(pg): [member
                          for member
                          in membersOfPG[str(pg)]
                          if member
                          in all_members]
                for pg
                in coalitionPGs['coalition']}
    oppo_pgs = {str(pg): [member
                          for member
                          in membersOfPG[str(pg)]
                          if member
                          in all_members]
                for pg
                in coalitionPGs['opposition']}

    coal_members = sum([len(member) for member in coal_pgs.values()])
    oppo_members = sum([len(member) for member in oppo_pgs.values()])

    kol = 100.0 / float(coal_members + oppo_members)

    seats = [{'party': Organization.objects.get(id_parladata=pg_id).getOrganizationData(),
              'seats': len(members_list), 'coalition': 'coalition'}
             for pg_id, members_list
             in coal_pgs.items()
             if len(members_list) > 0
             ] + [{'party': Organization.objects.get(id_parladata=pg_id).getOrganizationData(),
                   'seats': len(members_list), 'coalition': 'opposition'}
                  for pg_id, members_list
                  in oppo_pgs.items() if len(members_list) > 0]
    out['info'] = {role: [member
                          for member
                          in members_list]
                   for role, members_list
                   in members.items()}
    out['ratio'] = {'coalition': coal_members * kol,
                    'opposition': oppo_members * kol}
    out['seats_per_pg'] = list(reversed(sorted(seats,
                                               key=lambda s: s['seats'])))
    out['sessions'] = [{'id': session['id'],
                        'name': session['name'],
                        'date': session['start_time']} for session in sessions]
    out['name'] = name
    final_response = saveOrAbortNew(
        WorkingBodies,
        created_for=date_of,
        organization=Organization.objects.get(id_parladata=org_id),
        president=Person.objects.get(id_parladata=out['info']['president'][0]),
        vice_president=out['info']['vice_president'],
        members=out['info']['members'],
        viceMember=out['info']['viceMember'],
        coal_ratio=coal_members*kol,
        oppo_ratio=oppo_members*kol,
        seats=list(reversed(sorted(seats, key=lambda s: s['seats']))),
        sessions=[session['id'] for session in sessions],
    )
    return JsonResponse(out)


def getWorkingBodies(request, org_id, date_=None):
    """
    * @api {get} getWorkingBodies/{org_id}/{?date} Gets specific working bodie
    * @apiName getWorkingBodies
    * @apiGroup PGs
    * @apiDescription This function returns detailed data about specific working bodie
    * @apiParam {Integer} org_id Parladata id for working bodie
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} info
    * @apiSuccess {Object[]} info.vice_president Vice presidents of working bodie
    * @apiSuccess {Boolean} info.vice_president.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} info.vice_president.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} info.vice_president.name MP's full name.
    * @apiSuccess {String} info.vice_president.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} info.vice_president.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} info.vice_president.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} info.vice_president.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} info.vice_president.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} info.vice_president.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} info.vice_president.party.name The party's name.
    * @apiSuccess {String} info.vice_president.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} info.vice_president.id The person's Parladata id.
    * @apiSuccess {Boolean} info.vice_president.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Object} info.vice_president.party The organization object.
    * @apiSuccess {String} info.vice_president.party.acronym PG's acronym
    * @apiSuccess {Boolean} info.vice_president.party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} info.vice_president.party.id PG's Parladata id.
    * @apiSuccess {String} info.vice_president.party.name PG's name

    * @apiSuccess {Object} info.president President of working bodie
    * @apiSuccess {Boolean} info.president.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} info.president.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} info.president.name MP's full name.
    * @apiSuccess {String} info.president.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} info.president.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} info.president.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} info.president.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} info.president.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} info.president.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} info.president.party.name The party's name.
    * @apiSuccess {String} info.president.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} info.president.id The person's Parladata id.
    * @apiSuccess {Boolean} info.president.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Object} info.president.party The organization object.
    * @apiSuccess {String} info.president.party.acronym PG's acronym
    * @apiSuccess {Boolean} info.president.party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} info.president.party.id PG's Parladata id.
    * @apiSuccess {String} info.president.party.name PG's name

    * @apiSuccess {Object[]} info.members Members of working bodie
    * @apiSuccess {Boolean} info.members.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} info.members.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} info.members.name MP's full name.
    * @apiSuccess {String} info.members.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} info.members.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} info.members.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} info.members.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} info.members.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} info.members.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} info.members.party.name The party's name.
    * @apiSuccess {String} info.members.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} info.members.id The person's Parladata id.
    * @apiSuccess {Boolean} info.members.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Object} info.members.party The organization object.
    * @apiSuccess {String} info.members.party.acronym PG's acronym
    * @apiSuccess {Boolean} info.members.party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} info.members.party.id PG's Parladata id.
    * @apiSuccess {String} info.members.party.name PG's name

    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object} ratio Ratio of percentage of coalition and opposition.
    * @apiSuccess {String} ratio.coalition Percentage of coalition members
    * @apiSuccess {String} ratio.opposition Opposition of coalition members

    * @apiSuccess {Object[]} seats_per_pg The organization object.
    * @apiSuccess {String} seats_per_pg.party.acronym PG's acronym
    * @apiSuccess {Boolean} seats_per_pg.party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} seats_per_pg.party.id PG's Parladata id.
    * @apiSuccess {String} seats_per_pg.party.name PG's name.
    
    * @apiSuccess {Object[]} session The session object.
    * @apiSuccess {String} session.name Name of session.
    * @apiSuccess {Date} session.date_ts Date and time of session.
    * @apiSuccess {Date} session.date Date of session.
    * @apiSuccess {Date} session.updated_at Date of last update.
    * @apiSuccess {Integer} session.session.id Id of session.
    * @apiSuccess {Boolean} session.session.in_review Return true or false if session is in review.
    * @apiSuccess {Object[]} session.orgs Organization object
    * @apiSuccess {String} session.orgs.acronym Organization acronym
    * @apiSuccess {Boolean} session.orgs.is_coalition True of False if organization is in coalition
    * @apiSuccess {Integer} session.orgs.id Id of organization
    * @apiSuccess {Integer} session.orgs.name Name of organization
    * @apiSuccess {Object[]} session.org Organization object
    * @apiSuccess {String} session.org.acronym Organization acronym
    * @apiSuccess {Boolean} session.org.is_coalition True of False if organization is in coalition
    * @apiSuccess {Integer} session.org.id Id of organization
    * @apiSuccess {Integer} session.org.name Name of organization

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getWorkingBodies/21
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getWorkingBodies/21/12.12.2015

    * @apiSuccessExample {json} Example response:

    {  
   "info":{  
      "vice_president":[  
         {  
            "is_active":false,
            "district":[  
               100
            ],
            "name":"Simon Zajc",
            "gov_id":"P293",
            "gender":"m",
            "party":{  
               "acronym":"SMC",
               "is_coalition":true,
               "id":1,
               "name":"PS Stranka modernega centra"
            },
            "type":"mp",
            "id":87,
            "has_function":false
         },
         {  
            "is_active":false,
            "district":[  
               103
            ],
            "name":"Violeta Tomić",
            "gov_id":"P289",
            "gender":"f",
            "party":{  
               "acronym":"Levica",
               "is_coalition":false,
               "id":8,
               "name":"PS Levica"
            },
            "type":"mp",
            "id":80,
            "has_function":false
         }
      ],
      "president":{  
         "is_active":false,
         "district":[  
            12
         ],
         "name":"Tomaž Lisec",
         "gov_id":"P187",
         "gender":"m",
         "party":{  
            "acronym":"SDS",
            "is_coalition":false,
            "id":5,
            "name":"PS Slovenska Demokratska Stranka"
         },
         "type":"mp",
         "id":53,
         "has_function":false
      },
      "members":[  
         {  
            "is_active":false,
            "district":[  
               40
            ],
            "name":"Benedikt Kopmajer",
            "gov_id":"P261",
            "gender":"m",
            "party":{  
               "acronym":"DeSUS",
               "is_coalition":true,
               "id":3,
               "name":"PS Demokratska Stranka Upokojencev Slovenije"
            },
            "type":"mp",
            "id":41,
            "has_function":false
         },
         {  
            "is_active":false,
            "district":[  
               44
            ],
            "name":"Bojan Podkrajšek",
            "gov_id":"P277",
            "gender":"m",
            "party":{  
               "acronym":"SDS",
               "is_coalition":false,
               "id":5,
               "name":"PS Slovenska Demokratska Stranka"
            },
            "type":"mp",
            "id":64,
            "has_function":false
         },
         {  
            "is_active":false,
            "district":[  
               14
            ],
            "name":"Vojka Šergan",
            "gov_id":"P285",
            "gender":"f",
            "party":{  
               "acronym":"SMC",
               "is_coalition":true,
               "id":1,
               "name":"PS Stranka modernega centra"
            },
            "type":"mp",
            "id":74,
            "has_function":false
         }
      ],
      "viceMember":[  

      ]
   },
   "created_for":"20.09.2017",
   "ratio":{  
      "coalition":58.8235294117647,
      "opposition":41.1764705882353
   },
   "sessions":[  
      {  
         "votes":false,
         "name":"22. redna seja",
         "orgs":[  
            {  
               "acronym":"",
               "is_coalition":false,
               "id":21,
               "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
            }
         ],
         "date":"7. 9. 2017",
         "org":{  
            "acronym":"",
            "is_coalition":false,
            "id":21,
            "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
         },
         "date_ts":"2017-09-07T02:00:00",
         "speeches":false,
         "updated_at":[  
            "7. 9. 2017"
         ],
         "in_review":false,
         "id":9719
      },
      {  
         "votes":false,
         "name":"64. nujna seja",
         "orgs":[  
            {  
               "acronym":"",
               "is_coalition":false,
               "id":21,
               "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
            }
         ],
         "date":"5. 9. 2017",
         "org":{  
            "acronym":"",
            "is_coalition":false,
            "id":21,
            "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
         },
         "date_ts":"2017-09-05T02:00:00",
         "speeches":false,
         "updated_at":[  
            "5. 9. 2017"
         ],
         "in_review":false,
         "id":9707
      },
      {  
         "votes":false,
         "name":"63. nujna seja",
         "orgs":[  
            {  
               "acronym":"",
               "is_coalition":false,
               "id":21,
               "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
            }
         ],
         "date":"5. 7. 2017",
         "org":{  
            "acronym":"",
            "is_coalition":false,
            "id":21,
            "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
         },
         "date_ts":"2017-07-05T02:00:00",
         "speeches":true,
         "updated_at":"21. 7. 2017",
         "in_review":false,
         "id":9672
      },
      {  
         "votes":false,
         "name":"62. nujna seja",
         "orgs":[  
            {  
               "acronym":"",
               "is_coalition":false,
               "id":21,
               "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
            }
         ],
         "date":"29. 6. 2017",
         "org":{  
            "acronym":"",
            "is_coalition":false,
            "id":21,
            "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
         },
         "date_ts":"2017-06-29T02:00:00",
         "speeches":true,
         "updated_at":"21. 7. 2017",
         "in_review":false,
         "id":9654
      }
      {  
         "votes":false,
         "name":"1. nujna seja",
         "orgs":[  
            {  
               "acronym":"",
               "is_coalition":false,
               "id":21,
               "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
            }
         ],
         "date":"12. 9. 2014",
         "org":{  
            "acronym":"",
            "is_coalition":false,
            "id":21,
            "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
         },
         "date_ts":"2014-09-12T02:00:00",
         "speeches":true,
         "updated_at":"8. 1. 2017",
         "in_review":false,
         "id":6415
      }
   ],
   "created_at":"20.09.2017",
   "seats_per_pg":[  
      {  
         "party":{  
            "acronym":"SMC",
            "is_coalition":true,
            "name":"PS Stranka modernega centra",
            "id":1
         },
         "coalition":"coalition",
         "seats":7
      },
      {  
         "party":{  
            "acronym":"SDS",
            "is_coalition":false,
            "name":"PS Slovenska Demokratska Stranka",
            "id":5
         },
         "coalition":"opposition",
         "seats":4
      }
   ],
   "organization":{  
      "acronym":"",
      "is_coalition":false,
      "id":21,
      "name":"Odbor za kmetijstvo, gozdarstvo in prehrano"
   }
}
    """
    workingBodies = getPGCardModelNew(WorkingBodies, org_id, date_)
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
    sessions = [session.getSessionData()
                for session
                in Session.objects.filter(organizations__id_parladata=org_id,
                                          start_time__lte=date_of).order_by('-start_time')]

    for session in sessions:
        session.update({'votes': True if Vote.objects.filter(session__id_parladata=session['id']) else False,
                        'speeches': True if Speech.objects.filter(session__id_parladata=session['id']) else False})

    return JsonResponse({'organization': workingBodies.organization.getOrganizationData(),
                         'created_at': workingBodies.created_at.strftime(API_DATE_FORMAT),
                         'created_for': workingBodies.created_for.strftime(API_DATE_FORMAT),
                         'info': {'president': getPersonData(workingBodies.president.id_parladata),
                                  'vice_president': sorted([getPersonData(person)
                                                            for person
                                                            in workingBodies.vice_president],
                                                           key=lambda k: k['name']),
                                  'members': sorted([getPersonData(person)
                                                     for person
                                                     in workingBodies.members],
                                                    key=lambda k: k['name']),
                                  'viceMember': sorted([getPersonData(person)
                                                        for person
                                                        in workingBodies.viceMember],
                                                       key=lambda k: k['name'])},
                         'ratio': {'coalition': workingBodies.coal_ratio,
                                   'opposition': workingBodies.oppo_ratio},
                         'seats_per_pg': workingBodies.seats,
                         'sessions': sessions})


def getWorkingBodies_live(request, org_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
    url = API_URL+'/getOrganizationRolesAndMembers/'+org_id+(('/'+date_) if date_ else '')
    members = tryHard(url).json()
    out = {}
    name = members.pop('name')
    all_members = [member for role in members.values() for member in role]
    coalitionPGs = tryHard(API_URL+'/getCoalitionPGs/').json()
    membersOfPG = tryHard(API_URL+'/getMembersOfPGsOnDate/'+date_).json()
    sessions = tryHard(API_URL+'/getSessionsOfOrg/'+org_id+(('/'+date_) if date_ else '')).json()
    coal_pgs = {str(pg): [member
                          for member
                          in membersOfPG[str(pg)]
                          if member
                          in all_members]
                for pg
                in coalitionPGs['coalition']}
    oppo_pgs = {str(pg): [member
                          for member
                          in membersOfPG[str(pg)]
                          if member
                          in all_members]
                for pg in coalitionPGs['opposition']}

    coal_members = sum([len(member) for member in coal_pgs.values()])
    oppo_members = sum([len(member) for member in oppo_pgs.values()])

    kol = 100.0/float(coal_members+oppo_members)
    seats = [{'party': Organization.objects.get(id_parladata=pg_id).getOrganizationData(),
              'seats': len(members_list), 'coalition': 'coalition'}
             for pg_id, members_list
             in coal_pgs.items()
             if len(members_list) > 0] + [{'party': Organization.objects.get(id_parladata=pg_id).getOrganizationData(),
                                           'seats': len(members_list), 'coalition': 'opposition'}
                                          for pg_id, members_list
                                          in oppo_pgs.items()
                                          if len(members_list) > 0]

    out['info'] = {role: [getPersonData(member)
                          for member
                          in members_list]
                   for role, members_list
                   in members.items()}
    out['ratio'] = {'coalition': coal_members * kol,
                    'opposition': oppo_members * kol}
    out['seats_per_pg'] = list(reversed(sorted(seats, key=lambda s: s['seats'])))
    out['sessions'] = [{'id': session['id'],
                        'name': session['name'],
                        'date': session['start_time']}
                       for session
                       in sessions]
    out['name'] = name
    return JsonResponse(out)


def getTaggedBallots(request, pg_id, date_=None):
    """
    * @api {get} getTaggedBallots/{pg_id}/{?date} Gets all tagged ballots for specific organization
    * @apiName getTaggedBallots
    * @apiGroup PGs
    * @apiDescription This function returns the list of all tagged ballots for specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object[]} results List of ballots.
    * @apiSuccess {date} results.date The date in question.
    * @apiSuccess {Object[]} results.ballots Ballots the MP submitted on that day.
    * @apiSuccess {Integer} results.ballots.ballot_id Ballot's Parladata id.
    * @apiSuccess {String} results.ballots.option The ballot option ("za"/"proti"/"ni"/"kvorum").
    * @apiSuccess {String[]} results.ballots.tags List of tags this ballot was tagged with.
    * @apiSuccess {Integer} results.ballots.session_id Parladata id of the session where this ballot was submitted.
    * @apiSuccess {String} results.ballots.motion The text of the motion (what was the vote about).
    * @apiSuccess {Boolean} results.ballots.result Answers the question: Did the motion pass?
    * @apiSuccess {Integer} results.ballots.vote_id Parladata id of the vote this ballot belongs to.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getTaggedBallots/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getTaggedBallots/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"18.09.2017",
   "created_for":"18.09.2017",
   "results":[  
      {  
         "date":"18. 9. 2017",
         "ballots":[  
            {  
               "option":"za",
               "tags":[  
                  "Proceduralna glasovanja"
               ],
               "session_id":9743,
               "motion":"Dnevni red v celoti",
               "result":true,
               "vote_id":7416
            }
         ]
      },
      {  
         "date":"14. 9. 2017",
         "ballots":[  
            {  
               "option":"proti",
               "tags":[  
                  "Interpelacija"
               ],
               "session_id":9724,
               "motion":"Interpelacija o delu in odgovornosti ministrice za zdravje, Milojke Kolar Celarc - Glasovanje o interpelaciji - MZ Milojka Kolar Celarc",
               "result":false,
               "vote_id":7404
            }
         ]
      }
   ]
}
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    b = Ballot.objects.filter(org_voter__id_parladata=pg_id,
                              start_time__lte=date_of)
    b_s = [model_to_dict(i, fields=['vote', 'option', 'id_parladata'])
           for i
           in b]
    b_s = {bal['vote']: (bal['id_parladata'], bal['option']) for bal in b_s}
    org = Organization.objects.get(id_parladata=pg_id)
    org_data = {'party': org.getOrganizationData()}

    result = prepareTaggedBallots(date_of, b_s, org_data)

    return JsonResponse(result, safe=False)


@lockSetter
def setVocabularySizeALL(request, date_=None):
    """Setter function for analysis of vocabulary size of PG.
    """
    sw = WordAnalysis(count_of='groups', date_=date_)

    #if not sw.isNewSpeech:
    #    return JsonResponse({'alliswell': True,
    #                         'msg': 'Na ta dan ni bilo govorov'})

    # Vocabolary size
    all_score = sw.getVocabularySize()
    max_score, maxPGid = sw.getMaxVocabularySize()
    avg_score = sw.getAvgVocabularySize()
    date_of = sw.getDate()
    maxPG = Organization.objects.get(id_parladata=maxPGid)

    print '[INFO] saving vocabulary size'
    for p in all_score:
        org = Organization.objects.get(id_parladata=int(p['counter_id']))
        saveOrAbortNew(model=VocabularySize,
                       organization=org,
                       created_for=date_of,
                       score=int(p['coef']),
                       maxOrg=maxPG,
                       average=avg_score,
                       maximum=max_score)

    return JsonResponse({'alliswell': True, 'msg': 'shranjeno'})


def getVocabularySize(request, pg_id, date_=None):
    """
    * @api {get} getVocabularySize/{pg_id}/{?date} Gets data of analysis size of vocabulary for specific organization
    * @apiName getTaggedBallots
    * @apiGroup PGs
    * @apiDescription This function returns the size of vocabulary for specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object} results List of ballots.
    * @apiSuccess {Object} results.max Object for maximum size of vocabulary.
    * @apiSuccess {Float} results.max.score Maximum size of vocabulary.
    * @apiSuccess {Object} results.max.parties The PG with the maximum size of vocabulary.
    * @apiSuccess {String} results.max.parties.acronym PG's acronym
    * @apiSuccess {Boolean} results.max.parties.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} results.max.parties.id PG's Parladata id.
    * @apiSuccess {String} results.max.parties.name PG's name.
    * @apiSuccess {Float} results.average Average size of vocabulary.
    * @apiSuccess {Integer} results.score Score
    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getVocabularySize/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getVocabularySize/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
   "party":{  
      "acronym":"NeP - AČ",
      "is_coalition":false,
      "id":108,
      "name":"Nepovezani poslanec Andrej Čuš"
   },
   "created_at":"01.12.2016",
   "created_for":"14.11.2016",
   "results":{  
      "max":{  
         "score":127.347517730496,
         "parties":[  
            {  
               "acronym":"NeP - MBK",
               "is_coalition":false,
               "id":107,
               "name":"Nepovezana poslanka Mirjam Bon Klanjšček"
            }
         ]
      },
      "average":104.095736759989,
      "score":118
   }
}
    """
    card = getPGCardModelNew(VocabularySize, pg_id, date_)
    out = {
        'party': card.organization.getOrganizationData(),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'results': {
            'max': {
                'score': card.maximum,
                'parties': [card.maxOrg.getOrganizationData()]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getPGsIDs(request):
    """
    * @api {get} getTaggedBallots/{pg_id}/{?date} Gets all ids of all parlament groups
    * @apiName getPGsIDs
    * @apiGroup PGs
    * @apiDescription This function returns all ids of all parlament groups.
    * @apiSuccess {date} lastDate The date the last update of parlament groups
    * @apiSuccess {List[]} List List of all ids of parlament group.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getPGsIDs

    * @apiSuccessExample {json} Example response:
    {  
   "lastDate":"18.09.2017",
   "list":[  
      "109",
      "1",
      "3",
      "2",
      "5",
      "7",
      "6",
      "8"
   ]
}
    """
    output = []
    data = tryHard(API_URL+'/getAllPGs/')
    data = data.json()
    lastSession = Session.objects.all().order_by('-start_time')[0]
    output = {'list': [i for i in data],
              'lastDate': lastSession.start_time.strftime(API_DATE_FORMAT)}

    return JsonResponse(output, safe=False)


@csrf_exempt
@lockSetter
def setAllPGsStyleScoresFromSearch(request):
    """Setter for analysis style score.
    """
    if request.method == 'POST':
        post_data = json.loads(request.body)
        print post_data
        if post_data:
            save_statuses = []
            for score in post_data:
                org = Organization.objects.get(id_parladata=int(score['party']))
                date_of = datetime.today()
                save_statuses.append(saveOrAbortNew(
                    model=StyleScores,
                    created_for=date_of,
                    organization=org,
                    problematicno=float(score['problematicno']),
                    privzdignjeno=float(score['privzdignjeno']),
                    preprosto=float(score['preprosto']),
                    problematicno_average=float(score['problematicno_average']),
                    privzdignjeno_average=float(score['privzdignjeno_average']),
                    preprosto_average=float(score['preprosto_average'])
                ))
            return JsonResponse({'status': 'alliswell',
                                 'saved': save_statuses})
        else:
            return JsonResponse({'status': 'There\'s not data'})
    else:
        return JsonResponse({'status': 'It wasnt POST'})


def getStyleScoresPG(request, pg_id, date_=None):
    """
    * @api {get} getStyleScores/{pg_id}/{?date} Gets all style socre for specific organization
    * @apiName getStyleScores
    * @apiGroup PGs
    * @apiDescription This function returns style socre for specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results List of ballots.
    * @apiSuccess {Float} results.problematicno The resoult of style score "problematic".
    * @apiSuccess {Float} results.preprosto  The resoult of style score "simple".
    * @apiSuccess {Float} results.privzdignjeno The resoult of style score "raised".

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getStyleScores/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getStyleScores/1/12.12.2015

    * @apiSuccessExample {json} Example response:
{  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"01.03.2017",
   "created_for":"01.03.2017",
   "results":{  
      "problematicno":0.01409816852772803,
      "preprosto":0.061039753160307866,
      "privzdignjeno":0.055465651048477935
   }
}
    """
    card = getPGCardModelNew(StyleScores, int(pg_id), date_)

    privzdignjeno = 0
    problematicno = 0
    preprosto = 0

    if card.privzdignjeno != 0 and card.privzdignjeno_average != 0:
        privzdignjeno = card.privzdignjeno/card.privzdignjeno_average

    if card.problematicno != 0 and card.problematicno_average != 0:
        problematicno = card.problematicno/card.problematicno_average

    if card.preprosto != 0 and card.preprosto_average != 0:
        preprosto = card.preprosto/card.preprosto_average

    out = {
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'party': card.organization.getOrganizationData(),
        'results': {
            'privzdignjeno': privzdignjeno,
            'problematicno': problematicno,
            'preprosto': preprosto
        }
    }
    return JsonResponse(out, safe=False)


@csrf_exempt
@lockSetter
def setAllPGsTFIDFsFromSearch(request):
    """Setter for analysis TFIDF
    """
    if request.method == 'POST':
        post_data = json.loads(request.body)
        if post_data:
            save_statuses = []
            for score in post_data:
                org = Organization.objects.get(id_parladata=score['party']['id'])
                date_of = datetime.today()
                save_statuses.append(saveOrAbortNew(Tfidf,
                                                    organization=org,
                                                    created_for=date_of,
                                                    is_visible=False,
                                                    data=score['results']))

            return JsonResponse({'status': 'alliswell',
                                 'saved': save_statuses})
        else:
            return JsonResponse({'status': 'There\'s not data'})
    else:
        return JsonResponse({'status': 'It wasnt POST'})


def getTFIDF(request, party_id, date_=None):
    """
    * @api {get} getTFIDF/{pg_id}/{?date} Gets TFIDF scores.
    * @apiName getTFIDF
    * @apiGroup PGs
    * @apiDescription This function returns the list of TFIDF scores for specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results List of ballots.
    * @apiSuccess {String} results.term Term of TFIDF
    * @apiSuccess {Object} results.scores
    * @apiSuccess {Integer} results.tf
    * @apiSuccess {Integer} results.df
    * @apiSuccess {Float} results.tf-idf

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getTFIDF/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getTFIDF/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"27.02.2017",
   "created_for":"27.02.2017",
   "results":[  
      {  
         "term":"ZDoh",
         "scores":{  
            "tf":11,
            "df":7,
            "tf-idf":1.5714285714285714
         }
      },
      {  
         "term":"porotnica",
         "scores":{  
            "tf":24,
            "df":19,
            "tf-idf":1.263157894736842
         }
      }
   ]
}
    """
    card = getPGCardModelNew(Tfidf, int(party_id), is_visible=True, date=date_)

    out = {
        'party': card.organization.getOrganizationData(),
        'results': card.data,
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'created_at': card.created_at.strftime(API_DATE_FORMAT)
    }

    return JsonResponse(out)


@lockSetter
def setNumberOfQuestionsAll(request, date_=None):
    """Setts the number of parliamentary questions for all parlament groups
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()

    date_s = date_of.strftime(API_DATE_FORMAT)

    url = API_URL + '/getAllQuestions/' + date_s
    data = getDataFromPagerApi(url)
    url_pgs = API_URL + '/getAllPGs/' + date_s
    pgs_on_date = tryHard(url_pgs).json()
    url = API_URL + '/getMPs/' + date_s
    mps = tryHard(url).json()

    mpStatic = {}
    for mp in mps:
        mpStatic[str(mp['id'])] = getPersonData(str(mp['id']), date_s)

    allPGs = tryHard(API_URL+'/getAllPGsExt/').json().keys()

    pg_ids = [int(pg_id) for pg_id in pgs_on_date.keys()]
    authors = []
    for question in data:
        qDate = datetime.strptime(question['date'], '%Y-%m-%dT%X')
        qDate = qDate.strftime(API_DATE_FORMAT)
        try:
            person_data = mpStatic[str(question['author_id'])]
        except KeyError as e:
            person_data = getPersonData(str(question['author_id']), date_s)
            mpStatic[str(question['author_id'])] = person_data
        if person_data and person_data['party'] and person_data['party']['id']:
            authors.append(person_data['party']['id'])
        else:
            print 'person nima mpstatic: ', question['author_id']

    avg = len(authors)/float(len(pg_ids))
    question_count = Counter(authors)
    max_value = 0
    max_orgs = []
    for maxi in question_count.most_common(90):
        if max_value == 0:
            max_value = maxi[1]
        if maxi[1] == max_value:
            max_orgs.append(maxi[0])
        else:
            break
    is_saved = []
    for pg_id in pg_ids:
        org = Organization.objects.get(id_parladata=pg_id)
        is_saved.append(saveOrAbortNew(model=NumberOfQuestions,
                                       created_for=date_of,
                                       organization=org,
                                       score=question_count[pg_id],
                                       average=avg,
                                       maximum=max_value,
                                       maxOrgs=max_orgs))

    return JsonResponse({'alliswell': True,
                         'saved': is_saved})


def getNumberOfQuestions(request, pg_id, date_=None):
    """
    * @api {get} getNumberOfQuestions/{pg_id}/{?date} Gets all tagged ballots for specific organization
    * @apiName getNumberOfQuestions
    * @apiGroup PGs
    * @apiDescription This function returns the list of all tagged ballots for specific organization.
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object} results
    * @apiSuccess {Object} results.max Object of maximum of parliamentary questions.
    * @apiSuccess {Float} results.max.score Maximum size of parliamentary questions.
    * @apiSuccess {Object} results.max.parties The PG with the maximum size of vocabulary.
    * @apiSuccess {String} results.max.parties.acronym PG's acronym
    * @apiSuccess {Boolean} results.max.parties.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} results.max.parties.id PG's Parladata id.
    * @apiSuccess {String} results.max.parties.name PG's name.
    * @apiSuccess {Float} results.average Average of parliamentary questions.
    * @apiSuccess {Integer} results.score Score

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfQuestions/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfQuestions/1/12.12.2015

    * @apiSuccessExample {json} Example response:
   {  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"18.07.2017",
   "created_for":"18.07.2017",
   "results":{  
      "max":{  
         "score":2817,
         "parties":[  
            {  
               "acronym":"SDS",
               "is_coalition":false,
               "id":5,
               "name":"PS Slovenska Demokratska Stranka"
            }
         ]
      },
      "average":581.375,
      "score":254
   }
}
    """
    card = getPGCardModelNew(NumberOfQuestions, pg_id, date_)

    card_date = card.created_for.strftime(API_DATE_FORMAT)

    max_orgs = []
    for m_org in card.maxOrgs:
        org = Organization.objects.get(id_parladata=m_org)
        max_orgs.append(org.getOrganizationData())

    out = {
        'party': card.organization.getOrganizationData(),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card_date,
        'results': {
            'max': {
                'score': card.maximum,
                'parties': max_orgs
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getQuestionsOfPG(request, pg_id, date_=False):
    """
    * @api {get} getQuestionsOfPG/{pg_id}/{?date} Gets all parliamentary questions of specific parlament group
    * @apiName getQuestionsOfPG
    * @apiGroup PGs
    * @apiDescription This function returns all parliamentary questions of specific parlament group
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} all_authors 
    * @apiSuccess {Boolean} all_authors.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} all_authors.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} all_authors.person.name MP's full name.
    * @apiSuccess {String} all_authors.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} all_authors.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} all_authors.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} all_authors.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} all_authors.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} all_authors.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} all_authors.person.party.name The party's name.
    * @apiSuccess {String} all_authors.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} all_authors.person.id The person's Parladata id.
    * @apiSuccess {Boolean} all_authors.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    
    * @apiSuccess {Object[]} results
    * @apiSuccess {date} date The date of question
    * @apiSuccess {Object[]} question
    * @apiSuccess {Object[]} question.person
    * @apiSuccess {Boolean} question.person.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} question.person.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} question.person.person.name MP's full name.
    * @apiSuccess {String} question.person.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} question.person.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} question.person.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} question.person.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} question.person.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} question.person.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} question.person.person.party.name The party's name.
    * @apiSuccess {String} question.person.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} question.person.person.id The person's Parladata id.
    * @apiSuccess {Boolean} question.person.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    
    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getTaggedBallots/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getTaggedBallots/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
 {  
   "created_for":"7. 7. 2017",
   "all_recipients":[  
      "minister za infrastrukturo",
      "ministrica za izobraževanje znanost in šport",
      "ministrica za delo družino socialne zadeve in enake možnosti",
      "minister za obrambo",
      "ministrica za delo družino socialne zadeve in enake možnosti, minister za kmetijstvo gozdarstvo in prehrano",
      "ministrica za obrambo",
      "ministrica za zdravje, ministrica za delo družino socialne zadeve in enake možnosti",
      "minister za pravosodje",
      "ministrica za okolje in prostor",
      "ministrica za kulturo",
      "minister za gospodarski razvoj in tehnologijo",
      "ministrica za delo družino socialne zadeve in enake možnosti, minister za pravosodje",
      "ministrica za izobraževanje znanost in šport, minister za kulturo",
      "ministrica za notranje zadeve",
      "minister za kmetijstvo gozdarstvo in prehrano",
      "minister za finance",
      "ministrica za delo družino socialne zadeve in enake možnosti, minister za zunanje zadeve",
      "minister za javno upravo",
      "ministrica za zdravje, ministrica za obrambo",
      "minister za kmetijstvo gozdarstvo in prehrano, ministrica za okolje in prostor",
      "ministrica brez resorja pristojna za razvoj strateške projekte in kohezijo",
      "ministrica za finance",
      "minister za gospodarski razvoj in tehnologijo, ministrica za finance",
      "minister za infrastrukturo, ministrica za okolje in prostor",
      "minister za finance v funkciji ministra za gospodarski razvoj in tehnologijo",
      "minister za zunanje zadeve",
      "predsednik Vlade",
      "ministrica za okolje in prostor, minister za kmetijstvo gozdarstvo in prehrano",
      "minister za kulturo",
      "ministrica za zdravje"
   ],
   "all_authors":[  
      {  
         "name":"Klavdija Markež",
         "district":[  
            26
         ],
         "gender":"f",
         "is_active":false,
         "party":{  
            "acronym":"SMC",
            "id":1,
            "is_coalition":true,
            "name":"PS Stranka modernega centra"
         },
         "type":"mp",
         "id":56,
         "gov_id":"P271",
         "has_function":false
      },
      {  
         "name":"Franc Laj",
         "district":[  
            17
         ],
         "gender":"m",
         "is_active":false,
         "party":{  
            "acronym":"PS NP",
            "id":109,
            "is_coalition":false,
            "name":"PS nepovezanih poslancev "
         },
         "type":"mp",
         "id":50,
         "gov_id":"P267",
         "has_function":false
      },
      {  
         "name":"Mitja Horvat",
         "district":[  
            96
         ],
         "gender":"m",
         "is_active":false,
         "party":{  
            "acronym":"SMC",
            "id":1,
            "is_coalition":true,
            "name":"PS Stranka modernega centra"
         },
         "type":"mp",
         "id":33,
         "gov_id":"P257",
         "has_function":false
      }
   ],
   "created_at":"20.09.2017",
   "results":[  
      {  
         "date":"7. 7. 2017",
         "questions":[  
            {  
               "person":{  
                  "name":"Erika Dekleva",
                  "district":[  
                     86
                  ],
                  "gender":"f",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":16,
                  "gov_id":"P247",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"ministrica za obrambo",
               "title":"v zvezi z onesnaževanjem na Osrednjem vadišču slovenske vojske Poček",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005ed427c0ac5acb7598a32f500418261a7cb0e0a062cde3585a20ad690",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Andreja Katič",
                     "district":[  
                        37
                     ],
                     "ministry":{  
                        "acronym":"MO",
                        "id":136,
                        "is_coalition":true,
                        "name":"Ministrstvo za obrambo"
                     },
                     "gender":"f",
                     "is_active":false,
                     "party":{  
                        "acronym":"SD",
                        "id":7,
                        "is_coalition":true,
                        "name":"PS Socialni Demokrati"
                     },
                     "type":"ministry",
                     "id":38,
                     "gov_id":"P258",
                     "has_function":false
                  }
               ],
               "id":10658,
               "session_id":"Unknown"
            },
            {  
               "person":{  
                  "name":"Marko Ferluga",
                  "district":[  
                     83
                  ],
                  "gender":"m",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":21,
                  "gov_id":"P250",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"ministrica za notranje zadeve",
               "title":"v zvezi s spodbujanjem gospodarske dejavnosti na turističnih območjih",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005f525f759c12be98eb8d9125ec275748bf814765fe11cc4c30420155e",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Vesna Györkös Žnidar",
                     "district":null,
                     "ministry":{  
                        "acronym":"MNZ",
                        "id":135,
                        "is_coalition":true,
                        "name":"Ministrstvo za notranje zadeve"
                     },
                     "gender":"f",
                     "is_active":false,
                     "party":null,
                     "type":"ministry",
                     "id":1302,
                     "gov_id":"G1302",
                     "has_function":false
                  }
               ],
               "id":10659,
               "session_id":"Unknown"
            },
            {  
               "person":{  
                  "name":"Dragan Matić",
                  "district":[  
                     74
                  ],
                  "gender":"m",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":57,
                  "gov_id":"P272",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"predsednik Vlade",
               "title":"v zvezi s kulturnim turizmom v Republiki Sloveniji",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005e495ebf9d9a4e20d6fc4ced02738eb20f85e833f50134245f1cfcd05",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Miro Cerar",
                     "district":[  
                        103
                     ],
                     "ministry":{  
                        "acronym":"Vlada",
                        "id":126,
                        "is_coalition":true,
                        "name":"Vlada"
                     },
                     "gender":"m",
                     "is_active":false,
                     "party":{  
                        "acronym":"SMC",
                        "id":1,
                        "is_coalition":true,
                        "name":"PS Stranka modernega centra"
                     },
                     "type":"ministry",
                     "id":13,
                     "gov_id":"G13",
                     "has_function":false
                  }
               ],
               "id":10657,
               "session_id":"Unknown"
            },
            {  
               "person":{  
                  "name":"Marko Ferluga",
                  "district":[  
                     83
                  ],
                  "gender":"m",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":21,
                  "gov_id":"P250",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"minister za pravosodje",
               "title":"v zvezi z odgovornostjo za izpustitev storilca kaznivega dejanja Preprečitve uradnega dejanja uradni osebi in kršitev pravil cestnega prometa z dne 5. 7. 2017",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e005fe4ca106b0e69211de15cafbf4db7850b7bef83cb15544ab3f8a975a",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Goran Klemenčič",
                     "district":null,
                     "ministry":{  
                        "acronym":"MP",
                        "id":138,
                        "is_coalition":true,
                        "name":"Ministrstvo za pravosodje"
                     },
                     "gender":"m",
                     "is_active":false,
                     "party":null,
                     "type":"ministry",
                     "id":1303,
                     "gov_id":"G1303",
                     "has_function":false
                  }
               ],
               "id":10660,
               "session_id":"Unknown"
            }
         ]
      },
      {  
         "date":"18. 4. 2017",
         "questions":[  
            {  
               "person":{  
                  "name":"Ivan Škodnik",
                  "district":[  
                     40
                  ],
                  "gender":"m",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":76,
                  "gov_id":"P286",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"minister za kmetijstvo gozdarstvo in prehrano",
               "title":"v zvezi z zagotavljanjem možnosti za predelavo hlodovine v Sloveniji",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0050996dabab771a034b87412f2d5e511bdecb7167295f4b359f69b6435",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Dejan Židan",
                     "district":null,
                     "ministry":{  
                        "acronym":"MKGP",
                        "id":134,
                        "is_coalition":true,
                        "name":"Ministrstvo za kmetijstvo, gozdarstvo in prehrano"
                     },
                     "gender":"m",
                     "is_active":false,
                     "party":null,
                     "type":"ministry",
                     "id":90,
                     "gov_id":"G90",
                     "has_function":false
                  }
               ],
               "id":10334,
               "session_id":"Unknown"
            },
            {  
               "person":{  
                  "name":"Marko Ferluga",
                  "district":[  
                     83
                  ],
                  "gender":"m",
                  "is_active":false,
                  "party":{  
                     "acronym":"SMC",
                     "id":1,
                     "is_coalition":true,
                     "name":"PS Stranka modernega centra"
                  },
                  "type":"mp",
                  "id":21,
                  "gov_id":"P250",
                  "has_function":false
               },
               "recipient_orgs":[  

               ],
               "recipient_text":"minister za kulturo",
               "title":"v zvezi s strategijo upravljanja kulturne dediščine",
               "url":"http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0051b277dfb0926c5817e2903247d0e4b985c5e2c2b22fa3383ff748dc7",
               "session_name":"Unknown",
               "recipient_persons":[  
                  {  
                     "name":"Anton Peršak",
                     "district":null,
                     "ministry":{  
                        "acronym":"MK",
                        "id":133,
                        "is_coalition":true,
                        "name":"Ministrstvo za kulturo"
                     },
                     "gender":"m",
                     "is_active":false,
                     "party":null,
                     "type":"ministry",
                     "id":1432,
                     "gov_id":"G1432",
                     "has_function":false
                  }
               ],
               "id":10336,
               "session_id":"Unknown"
            }
         ]
      }
   ]
}
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = date_of.strftime(API_DATE_FORMAT)

    end_of_day = date_of + timedelta(days=1)
    questions = Question.objects.filter(start_time__lt=end_of_day,
                                        author_org__id_parladata=pg_id)

    staticData = tryHard(BASE_URL + '/utils/getAllStaticData/').json()
    personsStatic = staticData['persons']
    ministrStatic = staticData['ministrs']

    questions = questions.extra(select={'start_time_date': 'DATE(start_time)'})
    dates = list(set(list(questions.values_list('start_time_date', flat=True))))
    dates.sort()
    data = {date: [] for date in dates}
    all_authors = {}
    all_recipients = list(questions.values_list('recipient_text',
                                                flat=True))
    for question in questions:
        p_id = str(question.person.id_parladata)
        temp_data = question.getQuestionData(ministrStatic)
        author = personsStatic[p_id]
        all_authors[p_id] = author
        temp_data.update({'person': author})
        data[question.start_time_date].append(temp_data)

    out = [{'date': date.strftime(API_OUT_DATE_FORMAT),
            'questions': data[date]}
           for date in dates]

    org = Organization.objects.get(id_parladata=pg_id)
    org_data = org.getOrganizationData()
    result = {
        'results': list(reversed(out)),
        'created_for': out[-1]['date'] if out else date_,
        'created_at': date_,
        'party': org_data,
        'all_authors': all_authors.values(),
        'all_recipients': list(set(all_recipients)),
        }
    return JsonResponse(result, safe=False)


def getListOfPGs(request, date_=None, force_render=False):
    """
    * @api {get} getListOfPGs Gets all parlament groups
    * @apiName getListOfPGs
    * @apiGroup PGs
    * @apiDescription This function returns all parlament groups.

    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results
    * @apiSuccess {Float} results.intra_disunion Result of analysis of inta-disunion
    * @apiSuccess {Integer} results.number_of_amendments Result of analysis number of amendments
    * @apiSuccess {Float} results.privzdignjeno Result of analysis style score "rise"
    * @apiSuccess {Integer} results.vocabulary_size Result of analysis vocabulary size
    * @apiSuccess {Integer} results.number_of_questions Result of analysis number of questions
    * @apiSuccess {Integer} results.seat_count Result of number of seats in parlament
    * @apiSuccess {Float} results.presence_votes Result of analysis of presence on votes
    * @apiSuccess {Float} results.presence_sessions Result of analysis of presence on sessions
    * @apiSuccess {Float} results.problematicno Result of analysis of style score "problematic"
    * @apiSuccess {Float} results.preprosto Result of analysis of style score "simple"

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getListOfPGs


    * @apiSuccessExample {json} Example response:
    {  
   "data":[  
      {  
         "party":{  
            "acronym":"SMC",
            "is_coalition":true,
            "name":"PS Stranka modernega centra",
            "id":1
         },
         "results":{  
            "intra_disunion":0.5813533236000595,
            "number_of_amendments":135,
            "privzdignjeno":0.055465651048477935,
            "vocabulary_size":124,
            "number_of_questions":254,
            "seat_count":35,
            "presence_votes":92.7684051599534,
            "presence_sessions":94.2167236078696,
            "problematicno":0.01409816852772803,
            "preprosto":0.061039753160307866
         }
      },
      {  
         "party":{  
            "acronym":"SDS",
            "is_coalition":false,
            "name":"PS Slovenska Demokratska Stranka",
            "id":5
         },
         "results":{  
            "intra_disunion":2.19689804102997,
            "number_of_amendments":280,
            "privzdignjeno":0.04106208331786034,
            "vocabulary_size":102,
            "number_of_questions":2817,
            "seat_count":19,
            "presence_votes":66.4733604862916,
            "presence_sessions":83.7104723531316,
            "problematicno":0.01582043604458103,
            "preprosto":0.06005854467272461
         }
      },
      {  
         "party":{  
            "acronym":"DeSUS",
            "is_coalition":true,
            "name":"PS Demokratska Stranka Upokojencev Slovenije",
            "id":3
         },
         "results":{  
            "intra_disunion":2.8766187998167894,
            "number_of_amendments":9,
            "privzdignjeno":0.11774129845219254,
            "vocabulary_size":126,
            "number_of_questions":123,
            "seat_count":11,
            "presence_votes":88.5897572483105,
            "presence_sessions":94.3135320470314,
            "problematicno":0.03600796232003048,
            "preprosto":0.14625485569575708
         }
      },
      {  
         "party":{  
            "acronym":"SD",
            "is_coalition":true,
            "name":"PS Socialni Demokrati",
            "id":7
         },
         "results":{  
            "intra_disunion":3.861954387556319,
            "number_of_amendments":12,
            "privzdignjeno":0.11489519477220245,
            "vocabulary_size":125,
            "number_of_questions":165,
            "seat_count":6,
            "presence_votes":87.0055447001267,
            "presence_sessions":90.6800348040434,
            "problematicno":0.03194953607315688,
            "preprosto":0.12539864696681088
         }
      },
      {  
         "party":{  
            "acronym":"NSI",
            "is_coalition":false,
            "name":"PS Nova Slovenija",
            "id":6
         },
         "results":{  
            "intra_disunion":0.6328349191963298,
            "number_of_amendments":75,
            "privzdignjeno":0.09300856518783383,
            "vocabulary_size":122,
            "number_of_questions":283,
            "seat_count":6,
            "presence_votes":66.8784029038112,
            "presence_sessions":85.7142857142857,
            "problematicno":0.02936898259144798,
            "preprosto":0.12645125272103677
         }
      },
      {  
         "party":{  
            "acronym":"Levica",
            "is_coalition":false,
            "name":"PS Levica",
            "id":8
         },
         "results":{  
            "intra_disunion":4.326385742334801,
            "number_of_amendments":181,
            "privzdignjeno":0.10688668819409212,
            "vocabulary_size":117,
            "number_of_questions":516,
            "seat_count":5,
            "presence_votes":71.2885662431942,
            "presence_sessions":81.5584415584416,
            "problematicno":0.039053541047179265,
            "preprosto":0.1494215397402997
         }
      },
      {  
         "party":{  
            "acronym":"PS NP",
            "is_coalition":false,
            "name":"PS nepovezanih poslancev ",
            "id":109
         },
         "results":{  
            "intra_disunion":7.026884156470127,
            "number_of_amendments":5,
            "privzdignjeno":0.23519830984664467,
            "vocabulary_size":104,
            "number_of_questions":126,
            "seat_count":4,
            "presence_votes":61.8307622504537,
            "presence_sessions":83.1168831168831,
            "problematicno":0.08006720551803538,
            "preprosto":0.28066606227414975
         }
      },
      {  
         "party":{  
            "acronym":"IMNS",
            "is_coalition":false,
            "name":"PS italijanske in madžarske narodne skupnosti",
            "id":2
         },
         "results":{  
            "intra_disunion":7.58948799275034,
            "number_of_amendments":5,
            "privzdignjeno":0.4560700680451448,
            "vocabulary_size":102,
            "number_of_questions":28,
            "seat_count":2,
            "presence_votes":80.1043557168784,
            "presence_sessions":78.5714285714286,
            "problematicno":0.10991231475909181,
            "preprosto":0.47794791242129137
         }
      }
   ]
}

    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        key = date_
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
        key = date_

    c_data = cache.get('pg_list_' + key)
    if c_data and not force_render:
        data = c_data
    else:
        allPGs = tryHard(API_URL + '/getAllPGsExt/').json().keys()
        url = API_URL + '/getMembersOfPGsRanges/' + date_
        pgs = tryHard(url).json()[-1]['members']
        list_of_cards = [{'method': getPercentOFAttendedSessionPG,
                          'data_path': ('sessions', 'organization_value'),
                          'out_path': ('results', 'presence_sessions')},
                         {'method': getPercentOFAttendedSessionPG,
                          'data_path': ('votes', 'organization_value'),
                          'out_path': ('results', 'presence_votes')},
                         {'method': getDisunionOrgID,
                          'data_path': ('result', 'score'),
                          'out_path': ('results', 'intra_disunion')},
                         {'method': getVocabularySize,
                          'data_path': ('results', 'score'),
                          'out_path': ('results', 'vocabulary_size')},
                         {'method': getNumberOfQuestions,
                          'data_path': ('results', 'score'),
                          'out_path': ('results', 'number_of_questions')},
                         {'method': getNumberOfAmendmetsOfPG,
                          'data_path': ('result', 'score'),
                          'out_path': ('results', 'number_of_amendments')},
                         {'method': getStyleScoresPG,
                          'data_path': ('results', 'privzdignjeno'),
                          'out_path': ('results', 'privzdignjeno')},
                         {'method': getStyleScoresPG,
                          'data_path': ('results', 'preprosto'),
                          'out_path': ('results', 'preprosto')},
                         {'method': getStyleScoresPG,
                          'data_path': ('results', 'problematicno'),
                          'out_path': ('results', 'problematicno')},
                         ]
        data = []
        for pg, members in pgs.items():
            if pg in allPGs and members:
                pg_obj = {}
                pg_obj['results'] = {}
                pg_id = pg
                org = Organization.objects.get(id_parladata=pg)
                pg_obj['party'] = org.getOrganizationData()

                # load data from cards
                for card in list_of_cards:
                    print card
                    setCardData(pg_obj,
                                card['method'],
                                pg_id,
                                date_,
                                card['data_path'],
                                card['out_path'])

                pg_obj['results']['seat_count'] = len(members)

                data.append(pg_obj)
        data = sorted(data,
                      key=lambda k: k['results']['seat_count'],
                      reverse=True)
        cache.set('pg_list_' + key, data, 60 * 60 * 48)

    return JsonResponse({'data': data})


@lockSetter
def setPresenceThroughTime(request, party_id, date_=None):
    """Setter for analysis presence through time
    """
    if date_:
        fdate = datetime.strptime(date_, '%d.%m.%Y').date()
    else:
        fdate = datetime.now().date()

    url = API_URL + '/getBallotsCounterOfParty/' + party_id + '/' + fdate.strftime(API_DATE_FORMAT)
    data = tryHard(url).json()

    data_for_save = []

    for month in data:
        options = YES + NOT_PRESENT + AGAINST + ABSTAIN
        stats = sum([month[option] for option in options if option in month.keys()])
        not_member = month['total'] - stats
        presence = float(stats-sum([month[option] for option in NOT_PRESENT  if option in month.keys()])) / stats if stats else 0
        data_for_save.append({'date_ts': month['date_ts'],
                              'presence': presence * 100,
                              })

    org = Organization.objects.get(id_parladata=party_id)
    saved = saveOrAbortNew(model=PresenceThroughTime,
                           organization=org,
                           created_for=fdate,
                           data=data_for_save)

    return JsonResponse({'alliswell': True, 'status': 'OK', 'saved': saved})


def getPresenceThroughTime(request, party_id, date_=None):
    """
    * @api {get} getPresenceThroughTime/{pg_id}/{?date} Gets presence on sessions through time for specific organization
    * @apiName getPresenceThroughTime
    * @apiGroup PGs
    * @apiDescription This function returns presence on sessions through time for specific organization
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results
    * @apiSuccess {date} results.date_ts Date of analysis.
    * @apiSuccess {Float} results.presence Percent of presence of time on specific date.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getPresenceThroughTime/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getPresenceThroughTime/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
{  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"21.08.2017",
   "created_for":"21.08.2017",
   "results":[  
      {  
         "date_ts":"2014-08-01T00:00:00",
         "presence":96.07843137254902
      },
      {  
         "date_ts":"2014-09-01T00:00:00",
         "presence":93.7037037037037
      },
      {  
         "date_ts":"2014-10-01T00:00:00",
         "presence":93.05555555555556
      },
      {  
         "date_ts":"2014-11-01T00:00:00",
         "presence":96.0727969348659
      },
      {  
         "date_ts":"2014-12-01T00:00:00",
         "presence":93.12386156648452
      },
      {  
         "date_ts":"2015-01-01T00:00:00",
         "presence":92.52645502645503
      },
      {  
         "date_ts":"2015-02-01T00:00:00",
         "presence":94.94535519125684
      },
      {  
         "date_ts":"2015-03-01T00:00:00",
         "presence":88.62745098039215
      },
      {  
         "date_ts":"2015-04-01T00:00:00",
         "presence":87.72609819121448
      },
      {  
         "date_ts":"2015-05-01T00:00:00",
         "presence":90.42145593869732
      },
      {  
         "date_ts":"2015-06-01T00:00:00",
         "presence":91.22574955908289
      },
      {  
         "date_ts":"2015-07-01T00:00:00",
         "presence":98.47619047619047
      },
      {  
         "date_ts":"2015-09-01T00:00:00",
         "presence":94.28571428571428
      },
      {  
         "date_ts":"2015-10-01T00:00:00",
         "presence":90.10989010989012
      },
      {  
         "date_ts":"2015-11-01T00:00:00",
         "presence":94.80243161094225
      },
      {  
         "date_ts":"2015-12-01T00:00:00",
         "presence":95.33527696793003
      },
      {  
         "date_ts":"2016-01-01T00:00:00",
         "presence":89.1891891891892
      },
      {  
         "date_ts":"2016-02-01T00:00:00",
         "presence":92.06349206349206
      },
      {  
         "date_ts":"2016-03-01T00:00:00",
         "presence":90.53360125027908
      },
      {  
         "date_ts":"2016-04-01T00:00:00",
         "presence":91.27272727272727
      },
      {  
         "date_ts":"2016-05-01T00:00:00",
         "presence":91.4868804664723
      },
      {  
         "date_ts":"2016-06-01T00:00:00",
         "presence":89.07142857142857
      },
      {  
         "date_ts":"2016-07-01T00:00:00",
         "presence":96.67189952904238
      },
      {  
         "date_ts":"2016-09-01T00:00:00",
         "presence":91.32996632996633
      },
      {  
         "date_ts":"2016-10-01T00:00:00",
         "presence":94.5
      },
      {  
         "date_ts":"2016-11-01T00:00:00",
         "presence":94.18367346938776
      },
      {  
         "date_ts":"2016-12-01T00:00:00",
         "presence":96.03174603174604
      },
      {  
         "date_ts":"2017-01-01T00:00:00",
         "presence":88.57142857142857
      },
      {  
         "date_ts":"2017-02-01T00:00:00",
         "presence":92.62548262548262
      },
      {  
         "date_ts":"2017-03-01T00:00:00",
         "presence":92.66846361185983
      },
      {  
         "date_ts":"2017-04-01T00:00:00",
         "presence":91.49425287356323
      },
      {  
         "date_ts":"2017-05-01T00:00:00",
         "presence":95.13553657630895
      },
      {  
         "date_ts":"2017-06-01T00:00:00",
         "presence":89.45783132530121
      },
      {  
         "date_ts":"2017-07-01T00:00:00",
         "presence":92.52525252525253
      }
   ]
}
    """     
    card = getPGCardModelNew(PresenceThroughTime,
                             party_id,
                             date_)
    card_date = card.created_for.strftime(API_DATE_FORMAT)

    out = {
        'party': card.organization.getOrganizationData(),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card_date,
        'results': card.data
    }

    return JsonResponse(out, safe=False)


def getIntraDisunion(request):
    """
    * @api {get} getIntraDisunion/ Gets all data for analysis intra-disunion
    * @apiName getIntraDisunion
    * @apiGroup PGs
    * @apiDescription This function returns all data for analysis intra-disunion
   
    * @apiSuccess {Object} results 
    * @apiSuccess {Object} Name of PG 
    * @apiSuccess {String} results.organization.acronym PG's acronym
    * @apiSuccess {Boolean} results.organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} results.organization.id PG's Parladata id.
    * @apiSuccess {String} results.organization.name PG's name.

    * @apiSuccess {Object[]} votes List of votes
    * @apiSuccess {String} votes.text Text of vote
    * @apiSuccess {Integer} votes.id_parladata Id of the database parladata
    * @apiSuccess {String} votes.maximum Majority required for voting
    * @apiSuccess {List[]} votes.tag Tags of vote
    * @apiSuccess {Boolean} votes.result Result of vote
    * @apiSuccess {Date} votes.date Date of vote

    * @apiSuccess {List[]} all_tags All tags for votes

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getIntraDisunion

    * @apiSuccessExample {json} Example response:
{  
   "results":{  
      "NSI":{  
         "organization":{  
            "acronym":"NSI",
            "is_coalition":false,
            "id":6,
            "name":"PS Nova Slovenija"
         },
         "votes":[  
            {  
               "text":"Dnevni red v celoti",
               "id_parladata":6513,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":true,
               "date":"2014-08-01T12:16:54"
            },
            {  
               "text":"Proceduralni predlog za prekinitev 1. točke dnevnega reda",
               "id_parladata":6512,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":false,
               "date":"2014-08-01T12:43:48"
            },
            {  
               "text":"Sklep o imenovanju predsednika in podpredsednika Mandatno-volilne komisije - Sklep",
               "id_parladata":6511,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-01T12:49:10"
            },
            {  
               "text":"Poročilo o izidu predčasnih volitev v Državni zbor Republike Slovenije - Glasovanje o predlogu sklepa",
               "id_parladata":6510,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":true,
               "date":"2014-08-01T14:18:26"
            },
            {  
               "text":"Predlog za izvolitev predsednika Državnega zbora Republike Slovenije - Glasovanje o sestavi komisije",
               "id_parladata":6509,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-01T15:54:29"
            },
            {  
               "text":"Dnevni red v celoti",
               "id_parladata":6639,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":true,
               "date":"2014-08-25T12:06:57"
            },
            {  
               "text":"Predlog za izvolitev podpredsednika Državnega zbora - Glasovanje o sestavi komisije za tajno glasovanje (EPA 12 - VII, EPA 15 - VII)",
               "id_parladata":6638,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-25T12:26:05"
            },
            {  
               "text":"Odlok o ustanovitvi in nalogah delovnih teles Državnega zbora - Glasovanje",
               "id_parladata":6637,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":true,
               "date":"2014-08-25T20:16:36"
            },
            {  
               "text":"Sklep o imenovanju generalne sekretarke Državnega zbora - Glasovanje",
               "id_parladata":6636,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-25T20:37:48"
            },
            {  
               "text":"Sklep o imenovanju predsednikov in podpredsednikov delovnih teles Državnega zbora - Glasovanje",
               "id_parladata":6635,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-25T21:00:14"
            },
            {  
               "text":"Sklep o izvolitvi predsednika, podpredsednika in članov Komisije za nadzor obveščevalnih in varnostnih služb - Sklep o prestavitvi obravnave in odločanja na naslednjo sejo",
               "id_parladata":6634,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-25T21:09:06"
            },
            {  
               "text":"Dnevni red v celoti",
               "id_parladata":6633,
               "maximum":"0.0",
               "tag":[  
                  "Proceduralna glasovanja"
               ],
               "result":true,
               "date":"2014-08-28T12:04:07"
            },
            {  
               "text":"Obvestilo s Sklepom o pravici nadomeščanja poslanca Državnega zbora - Glasovanje",
               "id_parladata":6632,
               "maximum":"0.0",
               "tag":[  
                  "Mandatno-volilna komisija"
               ],
               "result":true,
               "date":"2014-08-28T12:06:27"
            }
         ]
      }
   },
   "all_tags": [
    "Komisija za nadzor javnih financ",
    "Kolegij predsednika Državnega zbora",
    "Komisija za narodni skupnosti",
    "Komisija za odnose s Slovenci v zamejstvu in po svetu",
    "Komisija za poslovnik",
    "Mandatno-volilna komisija",
    "Odbor za delo, družino, socialne zadeve in invalide",
    "Odbor za finance in monetarno politiko",
    "Odbor za gospodarstvo",
    "Odbor za infrastrukturo, okolje in prostor",
    "Odbor za izobraževanje, znanost, šport in mladino",
    "Odbor za kmetijstvo, gozdarstvo in prehrano",
    "Odbor za kulturo",
    "Odbor za notranje zadeve, javno upravo in lokalno samoupravo",
    "Odbor za obrambo",
    "Odbor za pravosodje",
    "Odbor za zadeve Evropske unije",
    "Odbor za zdravstvo",
    "Odbor za zunanjo politiko",
    "Preiskovalna komisija o ugotavljanju zlorab v slovenskem bančnem sistemu ter ugotavljanju vzrokov in",
    "Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investiciji",
    "Ustavna komisija",
    "Proceduralna glasovanja",
    "Zunanja imenovanja",
    "Poslanska vprašanja",
    "Komisija za nadzor obveščevalnih in varnostnih služb",
    "Preiskovalne komisije",
    "Komisija za peticije ter za človekove pravice in enake možnosti",
    "Interpelacija",
    " Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investicij"
    ]
    }
}
    """     
    out = {}
    votesData = {}
    tab = []
    ob = {}
    obs = {}
    dataOut = {}
    paginator = Paginator(Vote.objects.all().order_by('start_time'), 50)
    page = request.GET.get('page', 1)
    try:
        votespag = paginator.page(page)
    except PageNotAnInteger:
        votespag = paginator.page(1)
    except EmptyPage:
        votespag = paginator.page(paginator.num_pages)

    for vote in votespag:
        votesData[vote.id_parladata] = {'text': vote.motion,
                                        'result': vote.result,
                                        'date': vote.start_time,
                                        'tag': vote.tags,
                                        'id_parladata': vote.id_parladata}

    for vote in votespag:
        intraD = vote.vote_intradisunion.all()
        for intra in intraD:
            if intra.organization.acronym in out.keys():
                obs = votesData[vote.id_parladata].copy()
                obs['maximum'] = intra.maximum
                out[intra.organization.acronym]['votes'].append(obs)
            else:
                obj = votesData[vote.id_parladata].copy()
                obj['maximum'] = intra.maximum
                ob['organization'] = intra.organization.getOrganizationData()
                ob['votes'] = []
                ob['votes'].append(obj)
                out[intra.organization.acronym] = ob
                ob = {}
        tab.append({'text': vote.motion,
                    'result': vote.result,
                    'date': vote.start_time,
                    'tag': vote.tags,
                    'maximum': vote.intra_disunion,
                    'id_parladata': vote.id_parladata})

    out['DZ'] = {'organization': 'dz',
                 'votes': tab}
    dataOut['results'] = out
    dataOut['all_tags'] = list(Tag.objects.all().values_list('name',
                                                             flat=True))
    return JsonResponse(dataOut, safe=False)


def getIntraDisunionOrg(request, org_id, force_render=False):
    """
    * @api {get} getIntraDisunionOrg/{pg_id}/{?date} Gets all data for analysis intra-disunion for specific parlament group
    * @apiName getIntraDisunionOrg
    * @apiGroup PGs
    * @apiDescription This function returns data for analysis intra-disunion for specific parlament group
    * @apiParam {Integer} pg_id Parladata id for the PG in question.

    * @apiSuccess {Object[]} votes List of votes
    * @apiSuccess {String} votes.text Text of vote
    * @apiSuccess {Integer} votes.id_parladata Id of the database parladata
    * @apiSuccess {String} votes.maximum Majority required for voting
    * @apiSuccess {List[]} votes.tag Tags of vote
    * @apiSuccess {Boolean} votes.result Result of vote
    * @apiSuccess {Date} votes.date Date of vote

    * @apiSuccess {List[]} all_tags All tags for votes

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getIntraDisunionOrg/1

    * @apiSuccessExample {json} Example response:
    {  
   "results":[  
      {  
         "text":"Dnevni red v celoti",
         "id_parladata":6513,
         "maximum":0,
         "tag":[  
            "Proceduralna glasovanja"
         ],
         "result":true,
         "date":"2014-08-01T12:16:54"
      },
      {  
         "text":"Proceduralni predlog za prekinitev 1. točke dnevnega reda",
         "id_parladata":6512,
         "maximum":0,
         "tag":[  
            "Proceduralna glasovanja"
         ],
         "result":false,
         "date":"2014-08-01T12:43:48"
      }
   ],
   "all_tags":[  
      "Komisija za nadzor javnih financ",
      "Kolegij predsednika Državnega zbora",
      "Komisija za narodni skupnosti",
      "Komisija za odnose s Slovenci v zamejstvu in po svetu",
      "Komisija za poslovnik",
      "Mandatno-volilna komisija",
      "Odbor za delo, družino, socialne zadeve in invalide",
      "Odbor za finance in monetarno politiko",
      "Odbor za gospodarstvo",
      "Odbor za infrastrukturo, okolje in prostor",
      "Odbor za izobraževanje, znanost, šport in mladino",
      "Odbor za kmetijstvo, gozdarstvo in prehrano",
      "Odbor za kulturo",
      "Odbor za notranje zadeve, javno upravo in lokalno samoupravo",
      "Odbor za obrambo",
      "Odbor za pravosodje",
      "Odbor za zadeve Evropske unije",
      "Odbor za zdravstvo",
      "Odbor za zunanjo politiko",
      "Preiskovalna komisija o ugotavljanju zlorab v slovenskem bančnem sistemu ter ugotavljanju vzrokov in",
      "Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investiciji",
      "Ustavna komisija",
      "Proceduralna glasovanja",
      "Zunanja imenovanja",
      "Poslanska vprašanja",
      "Komisija za nadzor obveščevalnih in varnostnih služb",
      "Preiskovalne komisije",
      "Komisija za peticije ter za človekove pravice in enake možnosti",
      "Interpelacija",
      " Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investicij"
   ]
}"""
    out = {}
    votesData = {}
    ob = {}
    obj = {}
    ob['votes'] = []
    tab = []
    org = Organization.objects.get(id_parladata=org_id)
    acr = org.acronym
    votes = Vote.objects.all().order_by('start_time')
    for vote in votes:
        votesData[vote.id_parladata] = {'text': vote.motion,
                                        'result': vote.result,
                                        'date': vote.start_time,
                                        'tag': vote.tags,
                                        'classification': vote.classification,
                                        'id_parladata': vote.id_parladata}

    c_data = cache.get('pg_disunion' + org_id)
    if c_data and not force_render:
        out = c_data
    else:
        if int(org_id) == 95:
            for vote in votes:
                tab.append({'text': vote.motion,
                            'result': vote.result,
                            'date': vote.start_time,
                            'tag': vote.tags,
                            'classification': vote.classification,
                            'maximum': vote.intra_disunion,
                            'id_parladata': vote.id_parladata})
                out['results'] = {'organization': 'dz',
                             'votes': tab}

            out['results'] = sorted(out['results']['votes'],
                                   key=lambda k: k['maximum'])
            out['all_tags'] = list(Tag.objects.all().values_list('name',
                                                                 flat=True))
            out["classifications"] = VOTE_NAMES
            cache.set('pg_disunion' + org_id, out, 60 * 60 * 48)
        else:
            for vote in votes:
                intraD = IntraDisunion.objects.filter(vote=vote,
                                                      organization__id_parladata=org_id)
                for intra in intraD:
                    obj = votesData[vote.id_parladata].copy()
                    obj['maximum'] = float(intra.maximum)
                    ob['votes'].append(obj)
                    ob['organization'] = org.getOrganizationData()
                out['results'] = ob

            out['results'] = sorted(out['results']['votes'],
                                   key=lambda k: k['maximum'])
            out['all_tags'] = list(Tag.objects.all().values_list('name',
                                                                 flat=True))
            out["classifications"] = VOTE_NAMES
            cache.set('pg_disunion' + org_id, out, 60 * 60 * 48)

    return JsonResponse(out, safe=False)


def getAmendmentsOfPG(request, pg_id, date_=None):
    """
    * @api {get} getAmendmentsOfPG/{pg_id}/{?date} Gets all data for amendments for specific parlament group
    * @apiName getAmendmentsOfPG
    * @apiGroup PGs
    * @apiDescription This function returns data for amendments for specific parlament group
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} party The organization object.
    * @apiSuccess {String} party.acronym PG's acronym
    * @apiSuccess {Boolean} party.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} party.id PG's Parladata id.
    * @apiSuccess {String} party.name PG's name.

    * @apiSuccess {Object[]} results
    * @apiSuccess {date} results.date The date of last update.
    * @apiSuccess {Object[]} results.votes
    * @apiSuccess {Object} results.votes.session
    * @apiSuccess {String} results.votes.session.name Name of session.
    * @apiSuccess {Date} results.votes.session.date_ts Date and time of session.
    * @apiSuccess {Date} results.votes.session.date Date of session.
    * @apiSuccess {Date} results.votes.session.updated_at Date of last update.
    * @apiSuccess {Integer} results.votes.session.session.id Id of session.
    * @apiSuccess {Boolean} results.votes.session.session.in_review Return true or false if session is in review.
    * @apiSuccess {Object[]} results.votes.session.orgs Organization object
    * @apiSuccess {String} results.votes.session.orgs.acronym Organization acronym
    * @apiSuccess {Boolean} results.votes.session.orgs.is_coalition True of False if organization is in coalition
    * @apiSuccess {Integer} results.votes.session.orgs.id Id of organization
    * @apiSuccess {Integer} results.votes.session.orgs.name Name of organization
    * @apiSuccess {Object[]} results.votes.session.org Organization object
    * @apiSuccess {String} results.votes.session.org.acronym Organization acronym
    * @apiSuccess {Boolean} results.votes.session.org.is_coalition True of False if organization is in coalition
    * @apiSuccess {Integer} results.votes.session.org.id Id of organization
    * @apiSuccess {Integer} results.votes.session.org.name Name of organization

    * @apiSuccess {Object} results.votes.results
    * @apiSuccess {Integer} results.votes.results.abstain Number of MPs that abstain on voting.
    * @apiSuccess {Integer} results.votes.results.against Number of MPs that are against on voting.
    * @apiSuccess {Integer} results.votes.results.motion_id ID of motion.
    * @apiSuccess {String} results.votes.results.text Text of motion
    * @apiSuccess {String[]} results.votes.results.tags Array of tags of motion.
    * @apiSuccess {Boolean} results.votes.results.is_outlier Analaysis if person is outlier.
    * @apiSuccess {Boolean} results.votes.results.has_outliers Analaysis if session have outliers.
    * @apiSuccess {Integer} results.votes.results.not_present Number of MPs that were not present.
    * @apiSuccess {Integer} results.votes.results.votes_for Number of MPs that voted with yes.
    * @apiSuccess {Boolean} results.votes.results.result True or False if the motion was successful.

    * @apiSuccess {List[]} all_tags All tags for votes

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getAmendmentsOfPG/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getAmendmentsOfPG/1/12.12.2015

    * @apiSuccessExample {json} Example response:
    {  
  {  
   "party":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"19.09.2017",
   "created_for":"19.09.2017",
   "results":[  
      {  
         "date":"19. 9. 2017",
         "votes":[  
            {  
               "session":{  
                  "name":"33. redna seja",
                  "date_ts":"2017-09-18T02:00:00",
                  "updated_at":"19. 9. 2017",
                  "orgs":[  
                     {  
                        "acronym":"DZ",
                        "id":95,
                        "is_coalition":false,
                        "name":"Državni zbor"
                     }
                  ],
                  "date":"18. 9. 2017",
                  "org":{  
                     "acronym":"DZ",
                     "id":95,
                     "is_coalition":false,
                     "name":"Državni zbor"
                  },
                  "id":9743,
                  "in_review":false
               },
               "results":{  

               }
            },
            {  
               "session":{  
                  "name":"33. redna seja",
                  "date_ts":"2017-09-18T02:00:00",
                  "updated_at":"19. 9. 2017",
                  "orgs":[  
                     {  
                        "acronym":"DZ",
                        "id":95,
                        "is_coalition":false,
                        "name":"Državni zbor"
                     }
                  ],
                  "date":"18. 9. 2017",
                  "org":{  
                     "acronym":"DZ",
                     "id":95,
                     "is_coalition":false,
                     "name":"Državni zbor"
                  },
                  "id":9743,
                  "in_review":false
               }
            }
         ]
      }
   ],
   "all_tags":[  
      "Komisija za nadzor javnih financ",
      "Kolegij predsednika Državnega zbora",
      "Komisija za narodni skupnosti",
      "Komisija za odnose s Slovenci v zamejstvu in po svetu",
      "Komisija za poslovnik",
      "Mandatno-volilna komisija",
      "Odbor za delo, družino, socialne zadeve in invalide",
      "Odbor za finance in monetarno politiko",
      "Odbor za gospodarstvo",
      "Odbor za infrastrukturo, okolje in prostor",
      "Odbor za izobraževanje, znanost, šport in mladino",
      "Odbor za kmetijstvo, gozdarstvo in prehrano",
      "Odbor za kulturo",
      "Odbor za notranje zadeve, javno upravo in lokalno samoupravo",
      "Odbor za obrambo",
      "Odbor za pravosodje",
      "Odbor za zadeve Evropske unije",
      "Odbor za zdravstvo",
      "Odbor za zunanjo politiko",
      "Preiskovalna komisija o ugotavljanju zlorab v slovenskem bančnem sistemu ter ugotavljanju vzrokov in",
      "Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investiciji",
      "Ustavna komisija",
      "Proceduralna glasovanja",
      "Zunanja imenovanja",
      "Poslanska vprašanja",
      "Komisija za nadzor obveščevalnih in varnostnih služb",
      "Preiskovalne komisije",
      "Komisija za peticije ter za človekove pravice in enake možnosti",
      "Interpelacija",
      " Preiskovalna komisija za ugotavljanje politične odgovornosti nosilcev javnih funkcij pri investicij"
   ]
}
}
"""
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    org = Organization.objects.get(id_parladata=pg_id)
    amendments = org.amendments.filter(start_time__lte=date_of).order_by('-start_time')
    amendments = amendments.extra(select={'start_time_date': 'DATE(start_time)'})
    sessionsData = json.loads(getAllStaticData(None).content)['sessions']
    dates = list(set(list(amendments.values_list('start_time_date', flat=True))))
    dates.sort()
    data = {date: [] for date in dates}
    out = []
    for vote in amendments:
        results = {'motion_id': vote.id_parladata,
                   'text': vote.motion,
                   'votes_for': vote.votes_for,
                   'against': vote.against,
                   'abstain': vote.abstain,
                   'not_present': vote.not_present,
                   'result': vote.result,
                   'is_outlier': vote.is_outlier,
                   'tags': vote.tags,
                   'has_outliers': vote.has_outlier_voters}
        thisSession = sessionsData[str(vote.session.id_parladata)]
        data[vote.start_time_date].append({'session': thisSession,
                                           'results': results
                                           })
    out = [{'date': date.strftime(API_OUT_DATE_FORMAT),
            'votes': data[date]}
           for date in dates]

    tags = list(Tag.objects.all().values_list('name', flat=True))
    result = {
        'party': org.getOrganizationData(),
        'created_at': dates[-1].strftime(API_DATE_FORMAT) if dates else None,
        'created_for': dates[-1].strftime(API_DATE_FORMAT) if dates else None,
        'all_tags': tags,
        'results': list(reversed(out))
        }
    return JsonResponse(result, safe=False)


def getDisunionOrg(request):
    """
    * @api {get} getDisunionOrg Gets the data for analysis disunion for all parlament groups
    * @apiName getDisunionOrg
    * @apiGroup PGs
    * @apiDescription This function returns the data for analysis disunion for all parlament groups
    
    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Float} sum The resoult of analysis disunion for parlament group


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getDisunionOrg/1

    * @apiSuccessExample {json} Example response:
  [  
   {  
      "organization":{  
         "acronym":"PS NP",
         "is_coalition":false,
         "id":109,
         "name":"PS nepovezanih poslancev "
      },
      "sum":7.095302214241279
   },
   {  
      "organization":{  
         "acronym":"SMC",
         "is_coalition":true,
         "id":1,
         "name":"PS Stranka modernega centra"
      },
      "sum":0.5816681918410643
   },
   {  
      "organization":{  
         "acronym":"DeSUS",
         "is_coalition":true,
         "id":3,
         "name":"PS Demokratska Stranka Upokojencev Slovenije"
      },
      "sum":2.912466548013221
   },
   {  
      "organization":{  
         "acronym":"IMNS",
         "is_coalition":false,
         "id":2,
         "name":"PS italijanske in madžarske narodne skupnosti"
      },
      "sum":7.719928186714542
   },
   {  
      "organization":{  
         "acronym":"SDS",
         "is_coalition":false,
         "id":5,
         "name":"PS Slovenska Demokratska Stranka"
      },
      "sum":2.19749942730155
   },
   {  
      "organization":{  
         "acronym":"SD",
         "is_coalition":true,
         "id":7,
         "name":"PS Socialni Demokrati"
      },
      "sum":3.8524835427903024
   },
   {  
      "organization":{  
         "acronym":"NSI",
         "is_coalition":false,
         "id":6,
         "name":"PS Nova Slovenija"
      },
      "sum":0.6268701376419659
   },
   {  
      "organization":{  
         "acronym":"Levica",
         "is_coalition":false,
         "id":8,
         "name":"PS Levica"
      },
      "sum":4.345451825254088
   }
]
    """     
    result = []
    data = tryHard(API_URL + '/getAllPGs/').json()
    for org in data:
        ids = IntraDisunion.objects.filter(organization__id_parladata=org)
        el = ids.values_list('maximum', flat=True)
        if len(el) != 0:
            suma = sum(map(float, el))/el.count()
        else:
            suma = 0
        org_ = Organization.objects.get(id_parladata=org)
        out = {
            'organization': org_.getOrganizationData(),
            'sum': suma
        }
        result.append(out)
    return JsonResponse(result, safe=False)


def getDisunionOrgID(request, pg_id, date_=None):
    """
    * @api {get} getDisunionOrg Gets the data for analysis disunion for specific parlament groups
    * @apiName getDisunionOrg
    * @apiGroup PGs
    * @apiDescription This function returns the data for analysis disunion for specific parlament groups
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Float} sum The resoult of analysis disunion for parlament group


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getDisunionOrg/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getDisunionOrg/1/12.12.2015

    * @apiSuccessExample {json} Example response:
   {  
      "organization":{  
         "acronym":"PS NP",
         "is_coalition":false,
         "id":109,
         "name":"PS nepovezanih poslancev "
      },
      "sum":7.095302214241279
   }
    """     
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''

    suma, ids = getDisunionInOrgHelper(pg_id, date_of) 
    org_data = ids[0].organization.getOrganizationData() if ids else {}
    orgs = tryHard(API_URL + '/getAllPGs/').json().keys()

    data = []
    for org in orgs:
        val, dis = getDisunionInOrgHelper(org, date_of)
        data.append({'value': val,
                     'org_obj': dis[0].organization,
                     'org_id': org})

    maxDisunion = max(data, key=lambda x:x['value'] if x['value'] else 0)

    values = [i['value'] for i in data if i['value']]
    try:
        avg = float(sum(values))/len(values)
    except:
        avg = 0

    out = {'organization': org_data,
           'result': {
               'score': suma,
               'max': {
                   'pgs': [maxDisunion['org_obj'].getOrganizationData() if maxDisunion['org_obj'] else {}],
                   'score': maxDisunion['value']
                   },
               'average': avg
               }
            }
    return JsonResponse(out, safe=False)


def getNumberOfAmendmetsOfPG(request, pg_id, date_=None):
    """
    * @api {get} getNumberOfAmendmetsOfPG/{pg_id}/{?date} Gets number of amendments of specific organization 
    * @apiName getNumberOfAmendmetsOfPG
    * @apiGroup PGs
    * @apiDescription This function returns number of amendments of specific organization
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfAmendmetsOfPG/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfAmendmetsOfPG/1/12.12.2015    
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    orgs = tryHard(API_URL + '/getAllPGs/').json().keys()
    org = count = last_card_date = None
    data = []
    for org_id in orgs:            
        temp_org, temp_count, last_card = getAmendmentsCount(org_id, date_of)
        data.append({'value': temp_count,
                     'org_obj': temp_org,
                     'org_id': org_id})
        print org_id, pg_id, type(org_id), type(pg_id)
        if org_id == str(pg_id):
            print("FOUND")
            org = temp_org
            count = temp_count
            last_card_date = last_card

    maxAmendmets = max(data, key=lambda x:x['value'] if x['value'] else 0)

    values = [i['value'] for i in data if i['value']]
    if values:
        avg = float(sum(values))/len(values)
    else:
        avg = 0

    out = {'organization': org.getOrganizationData(),
           'created_at': datetime.now().strftime(API_DATE_FORMAT),
           'created_for': last_card_date.strftime(API_DATE_FORMAT),
           'result': {
               'score': count,
               'max': {
                   'pgs': [maxAmendmets['org_obj'].getOrganizationData() if maxAmendmets['org_obj'] else {}],
                   'score': maxAmendmets['value']
                   },
               'average': avg
               }
            }
    return JsonResponse(out, safe=False)


@lockSetter
def setPGMismatch(request, pg_id, date_=None):
    """Setter for analysis mismatch of parlament group
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()
        date_ = ''
    staticData = json.loads(getAllStaticData(None).content)
    personsData = staticData['persons']

    org = Organization.objects.get(id_parladata=pg_id)
    url = API_URL + '/getMembersOfPGsOnDate/' + date_
    memsOfPGs = tryHard(url).json()
    data = []
    for member in memsOfPGs[str(pg_id)]:
        mismatch = getPersonCardModelNew(MismatchOfPG, int(member), date_)
        data.append({'id': member,
                     'ratio': mismatch.data})
    
    saved = saveOrAbortNew(model=PGMismatch,
                           organization=org,
                           created_for=date_of,
                           data=data)
    return JsonResponse({'alliswell': True})


def getPGMismatch(request, pg_id, date_=None):
    """
    * @api {get} getPGMismatch/{pg_id}/{?date} Gets the all MPs of specific organization and returns the ratio of mismatch of PG
    * @apiName getPGMismatch
    * @apiGroup PGs
    * @apiDescription This function returns all MPs of specific organization and returns the ratio of mismatch of PG
    * @apiParam {Integer} pg_id Parladata id for the PG in question.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_for The date this card was created for
    * @apiSuccess {date} created_at The date on which this card was created
    
    * @apiSuccess {Object} organization The organization object.
    * @apiSuccess {String} organization.acronym PG's acronym
    * @apiSuccess {Boolean} organization.is_coalition Is this PG a member of the coalition?
    * @apiSuccess {Integer} organization.id PG's Parladata id.
    * @apiSuccess {String} organization.name PG's name.

    * @apiSuccess {Object[]} results 
    * @apiSuccess {Object} results.person MP's person object
    * @apiSuccess {Boolean} results.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.person.name MP's full name.
    * @apiSuccess {String} results.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.person.party.name The party's name.
    * @apiSuccess {String} results.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} results.person.id The person's Parladata id.
    * @apiSuccess {Boolean} results.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    
    * @apiSuccess {Float} results.ratio Ratio of MP, how does mismatch from PG
    

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getPGMismatch/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getPGMismatch/1/12.12.2015

    * @apiSuccessExample {json} Example response:
  {  
   "organization":{  
      "acronym":"SMC",
      "is_coalition":true,
      "id":1,
      "name":"PS Stranka modernega centra"
   },
   "created_at":"16.08.2017",
   "created_for":"16.08.2017",
   "results":[  
      {  
         "person":{  

         },
         "ratio":2.17821782178218
      },
      {  
         "person":{  
            "name":"Ivan Prelog",
            "district":[  
               52
            ],
            "gender":"m",
            "is_active":false,
            "party":{  
               "acronym":"SMC",
               "id":1,
               "is_coalition":true,
               "name":"PS Stranka modernega centra"
            },
            "type":"mp",
            "id":68,
            "gov_id":"P279",
            "has_function":false
         },
         "ratio":2.01972757162987
      },
      {  
         "person":{  
            "name":"Branko Zorman",
            "district":[  
               62
            ],
            "gender":"m",
            "is_active":false,
            "party":{  
               "acronym":"SMC",
               "id":1,
               "is_coalition":true,
               "name":"PS Stranka modernega centra"
            },
            "type":"mp",
            "id":89,
            "gov_id":"P295",
            "has_function":false
         },
         "ratio":1.63382988947622
      }
   ]
}
    """     
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    org = Organization.objects.get(id_parladata=pg_id)
    mismatch = getPGCardModelNew(PGMismatch, pg_id, date_)
    staticData = json.loads(getAllStaticData(None).content)
    personsData = staticData['persons']
    data = []
    for result in mismatch.data:
        data.append({'person': personsData[str(result['id'])],
                     'ratio': result['ratio']})
    data = sorted(data, key=lambda k: k['ratio'], reverse=True)
    out = {
        'organization': org.getOrganizationData(),
        'created_at': mismatch.created_at.strftime(API_DATE_FORMAT),
        'created_for': mismatch.created_for.strftime(API_DATE_FORMAT),
        'results': data
    }
    return JsonResponse(out, safe=False)
