# -*- coding: UTF-8 -*-
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models.expressions import Date

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
from parlalize.utils_ import (tryHard, lockSetter, prepareTaggedBallots,
                              getAllStaticData, setCardData, getPersonCardModelNew,
                              getPGCardModelNew, getPersonData)
from parlalize.settings import (API_URL, API_DATE_FORMAT, BASE_URL,
                                API_OUT_DATE_FORMAT, SETTER_KEY)
from parlaskupine.models import *
from parlaseje.models import Activity, Session, Vote, Speech, Question
from parlaposlanci.models import Person, MismatchOfPG
from parlaposlanci.views import getMPsList
from kvalifikatorji.scripts import (countWords, getCountListPG, getScores,
                                    problematicno, privzdignjeno, preprosto)


# Create your views here.
@lockSetter
def setBasicInfOfPG(request, pg_id, date_):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        url = API_URL + '/getBasicInfOfPG/' + str(pg_id) + '/' + date_
        data = tryHard(url).json()
    else:
        date_of = datetime.now().date()
        url = API_URL+'/getBasicInfOfPG/'+str(pg_id)+'/'+date_of
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
        url = API_URL + '/isVoteOnDay/' + date_
        isNewVote = tryHard(url).json()['isVote']
        print isNewVote
        if not isNewVote:
            return JsonResponse({'alliswell': True,
                                 'status': 'Ni glasovanja na ta dan',
                                 'saved': False})
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
    * @apiSuccess {Object[]} votes.maxPG The PG with the most attended voting events.
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

    * @apiSuccess {Object} party The PG with the most attended voting events.
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

    * @apiSuccess {Object} party The PG with the most attended voting events.
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

    speeches = speeches.annotate(day=Date("start_time",
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


def getMPStaticPersonData(id_, date_):
    try:
        url = BASE_URL + '/p/getMPStatic/' + str(id_) + '/' + date_
        return tryHard(url).json()['person']
    except:
        return {'id': id_}


def getMostMatchingThem(request, pg_id, date_=None):
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
    mostMatching = getPGCardModelNew(DeviationInOrganization, pg_id, date_)
    if not date_:
        date_ = ''
    out_r = []
    for result in mostMatching.data:
        out_r.append({
            'ratio': result['ratio'],
            'person': getMPStaticPersonData(int(result['id']), date_)})
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
    sw = WordAnalysis(count_of='groups', date_=date_)

    if not sw.isNewSpeech:
        return JsonResponse({'alliswell': True,
                             'msg': 'Na ta dan ni bilo govorov'})

    # Vocabolary size
    all_score = sw.getVocabularySize()
    max_score, maxPGid = sw.getMaxVocabularySize()
    avg_score = sw.getAvgVocabularySize()
    date_of = sw.getDate()
    maxPG = Organization.objects.get(id_parladata=maxPGid)

    print '[INFO] saving vocabulary size'
    for p in all_score:
        Organization.objects.get(id_parladata=int(p['counter_id']))
        saveOrAbortNew(model=VocabularySize,
                       organization=org,
                       created_for=date_of,
                       score=int(p['coef']),
                       maxOrg=maxPG,
                       average=avg_score,
                       maximum=max_score)

    return JsonResponse({'alliswell': True, 'msg': 'shranjeno'})


def getVocabularySize(request, pg_id, date_=None):

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


# get PGs IDs
def getPGsIDs(request):
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
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()

    date_s = date_of.strftime(API_DATE_FORMAT)

    url = API_URL + '/getAllQuestions/' + date_s
    data = tryHard(url).json()
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
    card = getPGCardModelNew(NumberOfQuestions,
                             pg_id,
                             date_)
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
                          'data_path': (),
                          'out_path': ('results', 'intra_disunion')},
                         {'method': getVocabularySize,
                          'data_path': ('results', 'score'),
                          'out_path': ('results', 'vocabulary_size')},
                         {'method': getNumberOfQuestions,
                          'data_path': ('results', 'score'),
                          'out_path': ('results', 'number_of_questions')},
                         {'method': getNumberOfAmendmetsOfPG,
                          'data_path': (),
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
    if date_:
        fdate = datetime.strptime(date_, '%d.%m.%Y').date()
    else:
        fdate = datetime.now().date()

    url = API_URL + '/getBallotsCounterOfParty/' + party_id + '/' + fdate.strftime(API_DATE_FORMAT)
    data = tryHard(url).json()

    data_for_save = []

    for month in data:
        stats = month['ni'] + month['za'] + month['proti'] + month['kvorum']
        not_member = month['total'] - stats
        presence = float(stats-month['ni']) / stats if stats else 0
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
                            'maximum': vote.intra_disunion,
                            'id_parladata': vote.id_parladata})
                out['DZ'] = {'organization': 'dz',
                             'votes': tab}

            out[str(acr)] = sorted(out[str(acr)]['votes'],
                                   key=lambda k: k['maximum'])
            out['all_tags'] = list(Tag.objects.all().values_list('name',
                                                                 flat=True))
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
                out[Organization.objects.get(id_parladata=org_id).acronym] = ob

            out[str(acr)] = sorted(out[str(acr)]['votes'],
                                   key=lambda k: k['maximum'])
            out['all_tags'] = list(Tag.objects.all().values_list('name',
                                                                 flat=True))
            cache.set('pg_disunion' + org_id, out, 60 * 60 * 48)

    return JsonResponse(out, safe=False)


def getAmendmentsOfPG(request, pg_id, date_=None):
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
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    ids = IntraDisunion.objects.filter(organization__id_parladata=pg_id,
                                       vote__start_time__lte=date_of)
    el = ids.values_list('maximum', flat=True)
    if len(el) != 0:
        suma = sum(map(float, el))/el.count()
    else:
        suma = 0
    return JsonResponse(suma, safe=False)


def getNumberOfAmendmetsOfPG(request, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    org = Organization.objects.get(id_parladata=pg_id)
    count = org.amendments.filter(start_time__lte=date_of).count()
    return JsonResponse(count, safe=False)


@lockSetter
def setPGMismatch(request, pg_id, date_=None):
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
