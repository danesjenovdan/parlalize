# -*- coding: UTF-8 -*-
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.core.cache import cache
from django.utils import dateparse

from scipy.stats import rankdata
from datetime import date, datetime, timedelta
from collections import Counter
from raven.contrib.django.raven_compat.models import client
from slugify import slugify

from parlalize.settings import (API_URL, API_DATE_FORMAT, API_OUT_DATE_FORMAT,
                                SETTER_KEY, LAST_ACTIVITY_COUNT, BASE_URL, FRONT_URL,
                                ISCI_URL, GLEJ_URL, YES, NOT_PRESENT, AGAINST, ABSTAIN,
                                NOTIFICATIONS_API)
from parlalize.utils_ import (tryHard, lockSetter, prepareTaggedBallots, findDatesFromLastCard,
                              getPersonData, getPersonCardModelNew, saveOrAbortNew, getDataFromPagerApi,
                              getPersonAmendmentsCount, getAllStaticData)
from utils.parladata_api import getVotersIDs
from kvalifikatorji.scripts import (numberOfWords, countWords, getScore,
                                    getScores, problematicno, privzdignjeno,
                                    preprosto, TFIDF, getCountList)
from parlaseje.models import Session, Tag, Question
from utils.speech import WordAnalysis
from utils.compass import getData as getCompassData
from .models import *
from parlaskupine.models import Organization, Compass

import numpy
import requests
import json
import string
import copy


def index(request):
    return JsonResponse({})


def getMPStaticPL(request, person_id, date_=None):
    """
    * @api {get} /p/getMPStatic/{id}/{?date} MP's static info
    * @apiName getMPStatic
    * @apiGroup MPs
    * @apiDescription This function returns an object with all
      "static" data belonging to an MP. By static we mean that it
      is entered and maintained by hand and rarely, if ever, changes.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results
    * @apiSuccess {Integer} results.voters Number of voters who voted for this MP at the last election.
    * @apiSuccess {String} results.acronym This MP's party acronym.
    * @apiSuccess {Integer} results.mandate Number of this MP's mandates in the national assembly (including their current one).
    * @apiSuccess {Integer} results.party_id This MP's party's Parladata (organization) id.
    * @apiSuccess {Object[]} results.groups List of groups this MP is a member of (other than their party). #TODO refactor
    * @apiSuccess {Integer} results.groups.id Group's Parladata (organization) id.
    * @apiSuccess {String} results.groups.group_name Group's name.
    * @apiSuccess {String} results.education A string describing the education of this person.
    * @apiSuccess {Object[]} results.working_bodies_functions
    * @apiSuccess {String} results.working_bodies_functions.role The person's role in this working body.
    * @apiSuccess {Object} results.working_bodies_functions.wb Working body object.
    * @apiSuccess {String} results.working_bodies_functions.wb.acronym Working body's acronym (usually an empty string).
    * @apiSuccess {Boolean} results.working_bodies_functions.wb.is_coalition Answers the question: Does this working body belong to the coalition?
    * @apiSuccess {Integer} results.working_bodies_functions.wb.id Working body's Parladata (organization) id.
    * @apiSuccess {String} results.working_bodies_functions.wb.name The working body's name.
    * @apiSuccess {String} results.previous_occupation MP's occupation before becoming an MP.
    * @apiSuccess {String} results.name MP's name.
    * @apiSuccess {String[]} results.district List of strings representing district names.
    * @apiSuccess {Integer} results.age MP's age calculated from their birthday.
    * @apiSuccess {Object[]} results.social An array containing the object with social keys. #TODO refactor
    * @apiSuccess {String} results.social.twitter MP's Twitter url.
    * @apiSuccess {String} results.social.facebook MP's Facebook url.
    * @apiSuccess {String} results.social.linkedin MP's Linkedin url.
    * @apiSuccess {String} results.party MP's party name.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getMPStatic/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getMPStatic/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": true,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "08.03.2017",
        "created_for": "06.08.2014",
        "results": {
            "voters": 919,
            "acronym": "ZL",
            "mandates": 1,
            "party_id": 8,
            "groups": [{
            "group_id": 9,
            "group_name": "Kolegij predsednika dr\u017eavnega zbora"
            }, {
            "group_id": 34,
            "group_name": "Delegacija Dr\u017eavnega zbora v Parlamentarni skup\u0161\u010dini Unije za Sredozemlje"
            }],
            "education": "diplomant univerzitetnega programa\r\n",
            "working_bodies_functions": [{
            "role": "vice_president",
            "wb": {
                "acronym": "",
                "is_coalition": false,
                "id": 10,
                "name": "Komisija za nadzor javnih financ"
            }
            }],
            "previous_occupation": "\u0161tudent",
            "name": "Luka Mesec",
            "district": ["Trbovlje"],
            "age": 29,
            "social": [{
            "twitter": "https://twitter.com/lukamesec",
            "facebook": "https://www.facebook.com/mesec.luka",
            "linkedin": null
            }],
            "party": "PS Zdru\u017eena Levica"
        }
    }
    """
    card = getPersonCardModelNew(MPStaticPL, person_id, date_)

    if card.twitter == 'False':
        print card.twitter

    wbfs = []
    for funct in card.working_bodies_functions:
        org = Organization.objects.filter(id_parladata=funct['org_id'])
        if org:
            wbfs.append({'wb': org[0].getOrganizationData(date_),
                         'role': funct['role']})

    data = {
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': {
            'voters': card.voters,
            'birth_date': card.birth_date,
            'mandates': card.mandates,
            'party_id': card.party.id_parladata,
            'acronym': card.acronym,
            'education': card.education,
            'previous_occupation': card.previous_occupation,
            'name': card.name,
            'points': card.points,
            'district': [District.objects.get(id_parladata=dist).name for dist in card.district] if card.district else [],
            'party': card.party_name,
            'social': [{'facebook': card.facebook if card.facebook != 'False' else None, 'twitter': card.twitter if card.twitter != 'False' else None, 'linkedin': card.linkedin if card.linkedin != 'False' else None}],
            'groups': [{'group_id': group.groupid, 'group_name': group.groupname} for group in card.mpstaticgroup_set.all()],
            'working_bodies_functions': wbfs,
        }
    }

    return JsonResponse(data)


def getPercentOFAttendedSession(request, person_id, date=None):
    """
    * @api {get} /p/getPresence/{id}/{?date} MP's presence
    * @apiName getPresence
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated presence scores. There are two scores, one for their presence
      at voting events and one for their presence at sessions overall. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results

    * @apiSuccess {Object} results.votes MP's calculated presence at voting events.
    * @apiSuccess {Object} results.votes.max MP (or MPs) who has the highest attendance and their score.
    * @apiSuccess {Float} results.votes.max.score Max MP's score.
    * @apiSuccess {Object[]} results.votes.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.votes.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.votes.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.votes.max.mps.name MP's full name.
    * @apiSuccess {String} results.votes.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.votes.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.votes.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.votes.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.votes.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.votes.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.votes.max.mps.party.name The party's name.
    * @apiSuccess {String} results.votes.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.votes.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.votes.average The average score for this metric accross the parliament.
    * @apiSuccess {Float} results.votes.score Score for the MP in question.

    * @apiSuccess {Object} results.sessions MP's calculated presence at sessions.
    * @apiSuccess {Object} results.sessions.max MP (or MPs) who has the highest attendance and their score.
    * @apiSuccess {Float} results.sessions.max.score Max MP's score.
    * @apiSuccess {Object[]} results.sessions.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.sessions.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.sessions.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.sessions.max.mps.name MP's full name.
    * @apiSuccess {String} results.sessions.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.sessions.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.sessions.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.sessions.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.sessions.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.sessions.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.sessions.max.mps.party.name The party's name.
    * @apiSuccess {String} results.sessions.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.sessions.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {Float} results.votes.average The average score for this metric accross the parliament.
    * @apiSuccess {Float} results.votes.score Score for the MP in question.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getPresence/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getPresence/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "21.03.2017",
        "created_for": "17.02.2017",
        "results": {
            "votes": {
            "max": {
                "score": 98.5804416403786,
                "mps": [{
                "is_active": false,
                "district": [8],
                "name": "Ur\u0161ka Ban",
                "gov_id": "P240",
                "gender": "f",
                "party": {
                    "acronym": "SMC",
                    "is_coalition": true,
                    "id": 1,
                    "name": "PS Stranka modernega centra"
                },
                "type": "mp",
                "id": 3,
                "has_function": false
                }]
            },
            "average": 80.5083236752256,
            "score": 76.9716088328076
            },
            "sessions": {
            "max": {
                "score": 100.0,
                "mps": [{
                "is_active": false,
                "district": [84],
                "name": "Vlasta Po\u010dkaj",
                "gov_id": "P303",
                "gender": "f",
                "party": {
                    "acronym": "SMC",
                    "is_coalition": true,
                    "id": 1,
                    "name": "PS Stranka modernega centra"
                },
                "type": "mp",
                "id": 2934,
                "has_function": false
                }, {
                "is_active": false,
                "district": [85],
                "name": "Teja Ljubi\u010d",
                "gov_id": "P304",
                "gender": "f",
                "party": {
                    "acronym": "SMC",
                    "is_coalition": true,
                    "id": 1,
                    "name": "PS Stranka modernega centra"
                },
                "type": "mp",
                "id": 2933,
                "has_function": false
                }, {
                "is_active": false,
                "district": [48],
                "name": "Jasna Murgel",
                "gov_id": "P274",
                "gender": "f",
                "party": {
                    "acronym": "SMC",
                    "is_coalition": true,
                    "id": 1,
                    "name": "PS Stranka modernega centra"
                },
                "type": "mp",
                "id": 60,
                "has_function": false
                }, {
                "is_active": false,
                "district": [66],
                "name": "Julijana Bizjak Mlakar",
                "gov_id": "P158",
                "gender": "f",
                "party": {
                    "acronym": "DeSUS",
                    "is_coalition": true,
                    "id": 3,
                    "name": "PS Demokratska Stranka Upokojencev Slovenije"
                },
                "type": "mp",
                "id": 5,
                "has_function": false
                }]
            },
            "average": 88.5490589303276,
            "score": 85.5072463768116
            }
        }
    }
    """
    equalVoters = getPersonCardModelNew(Presence, person_id, date)

    out  = {
        'person': getPersonData(person_id, date),
        'created_at': equalVoters.created_at.strftime(API_DATE_FORMAT),
        'created_for': equalVoters.created_for.strftime(API_DATE_FORMAT),
        'results': {
            "sessions":{
                "score": equalVoters.person_value_sessions,
                "average": equalVoters.average_sessions,
                "max": {
                    "mps": [getPersonData(person, date) for person in equalVoters.maxMP_sessions[:5]],
                    "score": equalVoters.maximum_sessions,
                }
            },
            "votes": {
                "score": equalVoters.person_value_votes,
                "average": equalVoters.average_votes,
                "max": {
                    "mps": [getPersonData(person, date) for person in equalVoters.maxMP_votes[:5]],
                    "score": equalVoters.maximum_votes,
                }
            }
        }
    }
    return JsonResponse(out)


def getNumberOfSpokenWords(request, person_id, date=None):
    """
    * @api {get} /p/getNumberOfSpokenWords/{id}/{?date} MP's number of spoken words
    * @apiName getNumberOfSpokenWords
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated number of spoken words. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results MP's number of spoken words.
    * @apiSuccess {Object} results.max MP (or MPs) who has the highest number of spoken words and their score.
    * @apiSuccess {Float} results.max.score Max MP's score.
    * @apiSuccess {Object[]} results.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.max.mps.name MP's full name.
    * @apiSuccess {String} results.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.max.mps.party.name The party's name.
    * @apiSuccess {String} results.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.average The average score for this metric accross the parliament.
    * @apiSuccess {Float} results.score Score for the MP in question.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getNumberOfSpokenWords/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getNumberOfSpokenWords/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "21.03.2017",
        "created_for": "20.03.2017",
        "results": {
            "max": {
            "score": 672449,
            "mps": [{
                "is_active": false,
                "district": [17],
                "name": "Jo\u017eef Horvat",
                "gov_id": "P020",
                "gender": "m",
                "party": {
                "acronym": "NSI",
                "is_coalition": false,
                "id": 6,
                "name": "PS Nova Slovenija"
                },
                "type": "mp",
                "id": 32,
                "has_function": false
            }]
            },
            "average": 177115,
            "score": 381389
        }
    }
    """

    card = getPersonCardModelNew(SpokenWords, person_id, date)

    results = {
        'person': getPersonData(person_id, date),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'results': {
            'score': card.score,
            'average': card.average,
            'max': {
                'mps': [
                    getPersonData(card.maxMP.id_parladata, date)
                ],
                'score': card.maximum
            }
        }
    }
    return JsonResponse(results)


def getLastActivity(request, person_id, date_=None):
    """
    * @api {get} /p/getLastActivity/{id}/{?date} MP's last activity
    * @apiName getLastActivity
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs "last activity".
      This includes all ballots cast, questions asked and speeches spoken in the past
      ten days. This function returns the activity as it was calculated for a given
      date, if no date is supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person
      was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in
      coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the
      president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results
    * @apiSuccess {date} results.date The date of the events in this object.
    * @apiSuccess {Object[]} results.events List of event objects for this date.

    * @apiSuccess {String} results.events.option The option on the ballot, if the event was
      a ballot.
    * @apiSuccess {Integer} results.session_id Parladata id of the session at which the event
      took place, if the event was a ballot.
    * @apiSuccess {Boolean} results.result Returns true if the motion was passed, if the event
      was a ballot.
    * @apiSuccess {String} results.vote_name The name of the vote / text of the motion, if the
      event was a ballot.
    * @apiSuccess {Integer} results.vote_id Parladata id of the vote, if the event was a ballot.

    * @apiSuccess {String} results.recipient_text Who was the question addressed to, if the
      event was a question.
    * @apiSuccess {String} results.title The title of the question, if the event was a question.
    * @apiSuccess {String} results.content_url The url to the PDF of the question, if the
      event was a question.
    * @apiSUccess {Object} results.session Session object, if the event was a question. Currently returns null.
    * @apiSuccess {Integer} results.question_id Parladata id of the question, if the event was
      a question.

    * @apiSuccess {Object} results.session Session object, if the event was a speech.
    * @apiSuccess {String} results.session.name Session name, if the event was a speech.
    * @apiSuccess {date} results.session.date_ts UTF-8 date, if the event was a speech.
    * @apiSuccess {Object[]} results.session.orgs List of organizations this session belongs to, if the event was a speech.
    * @apiSuccess {String} results.session.orgs.acronym Organization acronym, if the event was a speech.
    * @apiSuccess {Boolean} results.session.orgs.is_coalition If the event was a speech answers the question: Is this organization in coalition with the government?
    * @apiSuccess {Integer} results.session.orgs.id Parladata id of the organization, if the event was a speech.
    * @apiSuccess {String} results.session.orgs.name Name of the organization, if the event was a speech.
    * @apiSuccess {date} results.session.date Slovenian date of the session, if the event was a speech.
    * @apiSuccess {Object} results.session.org The primary organization for this session, if the event was a speech.
    * @apiSuccess {String} results.session.org.acronym Organization acronym, if the event was a speech.
    * @apiSuccess {Boolean} results.session.org.is_coalition If the event was a speech answers the question: Is this organization in coalition with the government?
    * @apiSuccess {Integer} results.session.org.id Parladata id of the organization, if the event was a speech.
    * @apiSuccess {String} results.session.org.name Name of the organization, if the event was a speech.
    * @apiSuccess {Integer} results.session.id Parladata id of the session, if the event ws a speech.

    * @apiSuccess {String} results.type Denotes the type of event (ballot/speech/question).

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getLastActivity/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getLastActivity/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "20. 3. 2017",
        "created_for": "20. 3. 2017",
        "results": [{
            "date": "20. 3. 2017",
            "events": [{
            "option": "za",
            "session_id": 9379,
            "result": true,
            "vote_name": "Dnevni red v celoti",
            "vote_id": 6900,
            "type": "ballot"
            }]
        }, {
            "date": "17. 3. 2017",
            "events": [{
            "recipient_text": "ministrica za zdravje",
            "title": "v zvezi z zakonskim omejevanjem vsebnosti transma\u0161\u010dob v \u017eivilh",
            "content_url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0052e10f59269cd589241144a04f18728b6e6935124c6df30d7331d1f5f",
            "session": null,
            "type": "question",
            "question_id": 10180
            }]
        }, {
            "date": "10. 3. 2017",
            "events": [{
            "session": {
                "name": "88. redna seja",
                "date_ts": "2017-03-10T01:00:00",
                "orgs": [{
                "acronym": "",
                "is_coalition": false,
                "id": 9,
                "name": "Kolegij predsednika dr\u017eavnega zbora"
                }],
                "date": "10. 3. 2017",
                "org": {
                "acronym": "",
                "is_coalition": false,
                "id": 9,
                "name": "Kolegij predsednika dr\u017eavnega zbora"
                },
                "id": 9358,
                "in_review": true
            },
            "speech_id": 1118501,
            "type": "speech"
            }]
        }]
    }
    """
    def getBallotData(ballot):
        vote = ballot.vote
        return {'option': ballot.option,
                'result': vote.result,
                'vote_name': vote.motion,
                'vote_id': vote.id_parladata,
                'type': 'ballot',
                'session_id': vote.session.id_parladata,
                }

    def getSpeechData(speech, sessions_data):
        this_session = sessions_data[str(speech.session.id_parladata)]
        return {'speech_id': speech.id_parladata,
                'type': 'speech',
                'session': this_session,
                'the_order': speech.the_order,
                }

    def getQuestionData(question, sessions_data):
        persons = [ministr.getJsonData() for ministr in question.recipient_persons_static.all()]
        orgs = []
        if question.session:
            this_session = sessions_data[str(question.session.id_parladata)]
        else:
            this_session = None
        for org in question.recipient_organizations.all():
            orgs.append(org.getOrganizationData())
        return {'question_id': question.id_parladata,
                'type': 'question',
                'session': this_session,
                'title': question.title,
                'recipient_text': question.recipient_text,
                'content_url': question.content_link,
                'recipient_persons': persons,
                'recipient_orgs': orgs,
                'type_of_question': question.type_of_question,
                }
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
    a = Activity.objects.filter(person__id_parladata=person_id)
    a = a.extra(select={'start_time_date': 'DATE(start_time)'})
    dates = list(set(list(a.values_list("start_time_date", flat=True))))
    dates.sort()
    limit = min([15, len(dates)])

    if limit != 0:
        a = a.filter(person__id_parladata=person_id,
                    start_time__gte=dates[-limit]).order_by('-start_time')

    staticData = json.loads(getAllStaticData(None).content)
    result = []
    dates = list(set(list(a.values_list("start_time_date", flat=True))))
    dates.sort()
    data = {date: [] for date in dates}
    for activity in a:
        act_obj = activity.get_child()
        if type(act_obj) == Ballot:
            data[activity.start_time_date].append(getBallotData(act_obj))
        elif type(act_obj) == Speech:
            data[activity.start_time_date].append(getSpeechData(act_obj, staticData['sessions']))
        elif type(act_obj) == Question:
            data[activity.start_time_date].append(getQuestionData(act_obj, staticData['sessions']))

    out = [{'date': date.strftime(API_OUT_DATE_FORMAT),
            'events': data[date]}
            for date in dates]

    if dates:
        card_date = dates[-1].strftime(API_OUT_DATE_FORMAT)
    else:
        card_date = datetime.now().strftime(API_OUT_DATE_FORMAT)

    result = {
        'created_at': card_date,
        'created_for': card_date,
        'person': getPersonData(person_id, date_),
        'results': list(reversed(out))
        }

    return JsonResponse(result, safe=False)


# TODO date
def getAllSpeeches(request, person_id, date_=None):
    """
    * @api {get} /p/getAllSpeeches/{id}/{?date} MP's speeches
    * @apiName getAllSpeeches
    * @apiGroup MPs
    * @apiDescription This function returns a list of all dates when the MP spoke
      as well as speech ids that happened on those days. The function returns the
      list as it was compiled on a given date, if no date is supplied the date is
      today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results MP's speeches.
    * @apiSuccess {date} results.date The date of the speech.
    * @apiSuccess {Object[]} results.speeches List of speeches that happened on this day.
    * @apiSuccess {String} results.speeches.session_name The name of the session at which the speech took place.
    * @apiSuccess {Integer} results.speech_id Parladata id of the speech.
    * @apiSuccess {Integer} results.session_id Parladata id of the session at which the speech took place.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getAllSpeeches/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getAllSpeeches/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "22. 11. 2016",
        "created_for": "28. 8. 2014",
        "results": [{
            "date": "28. 8. 2014",
            "speeches": [{
            "session_name": "2. izredna seja",
            "speech_id": 524522,
            "session_id": 5619
            }, {
            "session_name": "2. izredna seja",
            "speech_id": 524403,
            "session_id": 5619
            }]
        }, {
            "date": "25. 8. 2014",
            "speeches": [{
            "session_name": "1. izredna seja",
            "speech_id": 524582,
            "session_id": 5620
            }, {
            "session_name": "1. izredna seja",
            "speech_id": 524665,
            "session_id": 5620
            }, {
            "session_name": "1. izredna seja",
            "speech_id": 524690,
            "session_id": 5620
            }]
        }, {
            "date": "22. 8. 2014",
            "speeches": [{
            "session_name": "1. redna seja",
            "speech_id": 529141,
            "session_id": 5729
            }, {
            "session_name": "1. redna seja",
            "speech_id": 529131,
            "session_id": 5729
            }]
        }]
    }
    """
    if date_:
        fdate = datetime.strptime(date_, '%d.%m.%Y')
        speeches = Speech.getValidSpeeches(fdate)
        speeches = speeches.filter(person__id_parladata=person_id)
        speeches = [[speech for speech in speeches.filter(start_time__range=[t_date, t_date+timedelta(days=1)])] for t_date in speeches.filter(start_time__lte=fdate).order_by("start_time").datetimes('start_time', 'day')]
    else:
        fdate = datetime.now()
        speeches = Speech.getValidSpeeches(datetime.now())
        speeches = speeches.filter(person__id_parladata=person_id)
        speeches = [[speech for speech in speeches.filter(start_time__range=[t_date, t_date+timedelta(days=1)])] for t_date in speeches.order_by("start_time").datetimes('start_time', 'day')]
    out = []
    lastDay = None
    created_at = []
    for day in speeches:
        dayData = {"date": day[0].start_time.strftime(API_OUT_DATE_FORMAT), "speeches":[]}
        lastDay = day[0].start_time.strftime(API_OUT_DATE_FORMAT)
        for speech in day:
            created_at.append(speech.created_at)
            dayData["speeches"].append({
                "session_name": speech.session.name,
                "speech_id": speech.id_parladata,
                "session_id": speech.session.id_parladata})
        out.append(dayData)

    result = {
        'person': getPersonData(person_id, date_),
        'created_at': max(created_at).strftime(API_OUT_DATE_FORMAT) if created_at else datetime.today().strftime("API_DATE_FORMAT"),
        'created_for': lastDay if lastDay else datetime.today().strftime("API_DATE_FORMAT"),
        'results': list(reversed(out))
        }
    return JsonResponse(result, safe=False)





# Method return json with most similar voters to this voter
def getMostEqualVoters(request, person_id, date_=None):
    """
    * @api {get} /p/getMostEqualVoters/{id}/{?date} MP's most similar voters
    * @apiName getMostEqualVoters
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      top 5 most similar voters. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results List of 5 person objects representing MP's most similar voters.
    * @apiSuccess {Object} results.person MP's person object (comes with most calls).
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
    * @apiSuccess {Float} results.ratio The euclidean distance between the chosen MP and this one.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getMostEqualVoters/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getMostEqualVoters/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "03.11.2016",
        "created_for": "28.08.2014",
        "results": [{
            "person": {
            "is_active": false,
            "district": [103],
            "name": "Violeta Tomi\u0107",
            "gov_id": "P289",
            "gender": "f",
            "party": {
                "acronym": "ZL",
                "is_coalition": false,
                "id": 8,
                "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 80,
            "has_function": false
            },
            "ratio": 0.584624087008587
        }, {
            "person": {
            "is_active": false,
            "district": [49],
            "name": "Franc Tr\u010dek ",
            "gov_id": "P290",
            "gender": "m",
            "party": {
                "acronym": "ZL",
                "is_coalition": false,
                "id": 8,
                "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 82,
            "has_function": false
            },
            "ratio": 0.541776627164668
        }, {
            "person": {
            "is_active": false,
            "district": [76],
            "name": "Matja\u017e Han\u017eek",
            "gov_id": "P256",
            "gender": "m",
            "party": {
                "acronym": "ZL",
                "is_coalition": false,
                "id": 8,
                "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 31,
            "has_function": false
            },
            "ratio": 0.538931817860966
        }, {
            "person": {
            "is_active": false,
            "district": [83],
            "name": "Matej Ta\u0161ner Vatovec",
            "gov_id": "P288",
            "gender": "m",
            "party": {
                "acronym": "ZL",
                "is_coalition": false,
                "id": 8,
                "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 79,
            "has_function": false
            },
            "ratio": 0.494254483850995
        }, {
            "person": {
            "is_active": false,
            "district": [46],
            "name": "Branislav Raji\u0107",
            "gov_id": "P281",
            "gender": "m",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 70,
            "has_function": false
            },
            "ratio": 0.384675997982625
        }]
    }
    """
    equalVoters = getPersonCardModelNew(EqualVoters, person_id, date_)

    print equalVoters.person1.id_parladata

    out = {
        'created_at': equalVoters.created_at.strftime(API_DATE_FORMAT),
        'created_for': equalVoters.created_for.strftime(API_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': [
            {
                "ratio": equalVoters.votes1,
                "person": getPersonData(equalVoters.person1.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes2,
                "person": getPersonData(equalVoters.person2.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes3,
                "person": getPersonData(equalVoters.person3.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes4,
                "person": getPersonData(equalVoters.person4.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes5,
                "person": getPersonData(equalVoters.person5.id_parladata, date_),
            }
        ]
    }

    #data = getPersonCardModel(EqualVoters, person_id)
    return JsonResponse(out, safe=False)


# Method return json with less similar voters to this voter
def getLessEqualVoters(request, person_id, date_=None): # TODO refactor rename
    """
    * @api {get} /p/getLeastEqualVoters/{id}/{?date} MP's least similar voters
    * @apiName getLeastEqualVoters
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      top 5 least similar voters. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results List of 5 person objects representing MP's least similar voters.
    * @apiSuccess {Object} results.person MP's person object (comes with most calls).
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
    * @apiSuccess {Float} results.ratio The euclidean distance between the chosen MP and this one.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getLeastEqualVoters/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getLeastEqualVoters/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "03.11.2016",
        "created_for": "28.08.2014",
        "results": [{
            "person": {
            "is_active": false,
            "district": [60],
            "name": "Branko Grims",
            "gov_id": "P016",
            "gender": "m",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 26,
            "has_function": false
            },
            "ratio": -0.588580815327302
        }, {
            "person": {
            "is_active": false,
            "district": [94],
            "name": "An\u017ee Logar",
            "gov_id": "P238",
            "gender": "m",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 54,
            "has_function": false
            },
            "ratio": -0.475334337037446
        }, {
            "person": {
            "is_active": false,
            "district": [26],
            "name": "Suzana Lep \u0160imenko",
            "gov_id": "P268",
            "gender": "f",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 51,
            "has_function": false
            },
            "ratio": -0.475334337037446
        }, {
            "person": {
            "is_active": false,
            "district": [44],
            "name": "Bojan Podkraj\u0161ek",
            "gov_id": "P277",
            "gender": "m",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 64,
            "has_function": false
            },
            "ratio": -0.475334337037446
        }, {
            "person": {
            "is_active": false,
            "district": [7],
            "name": "Anja Bah \u017dibert",
            "gov_id": "P239",
            "gender": "f",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 2,
            "has_function": false
            },
            "ratio": -0.475334337037446
        }]
    }
    """
    equalVoters = getPersonCardModelNew(LessEqualVoters, person_id, date_)
    out = {
        'created_at': equalVoters.created_at.strftime(API_DATE_FORMAT),
        'created_for': equalVoters.created_for.strftime(API_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': [
            {
                "ratio": equalVoters.votes1,
                "person": getPersonData(equalVoters.person1.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes2,
                "person": getPersonData(equalVoters.person2.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes3,
                "person": getPersonData(equalVoters.person3.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes4,
                "person": getPersonData(equalVoters.person4.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes5,
                "person": getPersonData(equalVoters.person5.id_parladata, date_),
            }
        ]
    }

    #data = getPersonCardModel(EqualVoters, person_id)
    return JsonResponse(out, safe=False)


def getStyleScores(request, person_id, date_=None):
    """
    * @api {get} /p/getStyleScores/{id}/{?date} MP's style scores
    * @apiName getStyleScores
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      style scores. The function returns the scores as they were calculated
      for a given date. If no date is supplied it is assumed the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results MP's style scores.
    * @apiSuccess {Float} results.problematicno MP's "problematic" language score.
    * @apiSuccess {Float} results.preprosto MP's "simple" language score.
    * @apiSuccess {Float} results.privzdignjeno MP's "fancy" language score.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getStyleScores/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getStyleScores/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "02.11.2016",
        "created_for": "06.09.2014",
        "results": {
            "problematicno": 0.6451263190481497,
            "preprosto": 1.0269481824385878,
            "privzdignjeno": 0
        }
    }
    """
    card = getPersonCardModelNew(StyleScores, int(person_id), date_)

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
        'person': getPersonData(person_id, card.created_for.strftime(API_DATE_FORMAT)),
        'results': {
            'privzdignjeno': privzdignjeno,
            'problematicno': problematicno,
            'preprosto': preprosto
            # 'average': {
            #     'privzdignjeno': card.privzdignjeno_average*10000,
            #     'problematicno': card.problematicno_average*10000,
            #     'preprosto': card.preprosto_average*10000
            # }
        }
    }

    return JsonResponse(out, safe=False)


def getTFIDF(request, person_id, date_=None):
    """
    * @api {get} /p/getTFIDF/{id}/{?date} MP's top TFIDF terms
    * @apiName getTFIDF
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      top TFIDF terms. It returns between 10 and 15 terms, depending on the
      topical overlap of the top 15 terms. The function returns the score as
      it was calculated for a given date, if no date is supplied it is assumed
      the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results MP's top TFIDF words (between 10 and 15).
    * @apiSuccess {String} results.term The term in question.
    * @apiSuccess {Object} results.scores TFIDF scores
    * @apiSuccess {Integer} results.scores.tf Term frequency.
    * @apiSuccess {Integer} results.scores.df Document frequency.
    * @apiSuccess {Float} results.scores.tf-idf TF/DF.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getTFIDF/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getTFIDF/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "20.02.2017",
        "created_for": "20.02.2017",
        "results": [{
            "term": "transma\u0161\u010doba",
            "scores": {
            "tf": 27,
            "df": 30,
            "tf-idf": 0.9
            }
        }, {
            "term": "transma\u0161\u010doben",
            "scores": {
            "tf": 12,
            "df": 14,
            "tf-idf": 0.8571428571428571
            }
        }, {
            "term": "borznoposredni\u0161ki",
            "scores": {
            "tf": 47,
            "df": 59,
            "tf-idf": 0.7966101694915254
            }
        }, {
            "term": "soupravljanje",
            "scores": {
            "tf": 82,
            "df": 126,
            "tf-idf": 0.6507936507936508
            }
        }, {
            "term": "trgovalen",
            "scores": {
            "tf": 49,
            "df": 80,
            "tf-idf": 0.6125
            }
        }, {
            "term": "Cinven",
            "scores": {
            "tf": 35,
            "df": 63,
            "tf-idf": 0.5555555555555556
            }
        }, {
            "term": "borzen",
            "scores": {
            "tf": 60,
            "df": 114,
            "tf-idf": 0.5263157894736842
            }
        }, {
            "term": "Alpina",
            "scores": {
            "tf": 37,
            "df": 82,
            "tf-idf": 0.45121951219512196
            }
        }, {
            "term": "kislina",
            "scores": {
            "tf": 14,
            "df": 32,
            "tf-idf": 0.4375
            }
        }, {
            "term": "obvezni\u010dar",
            "scores": {
            "tf": 11,
            "df": 26,
            "tf-idf": 0.4230769230769231
            }
        }, {
            "term": "registrski",
            "scores": {
            "tf": 73,
            "df": 175,
            "tf-idf": 0.41714285714285715
            }
        }, {
            "term": "Lahovnikov zakon",
            "scores": {
            "tf": 20,
            "df": 49,
            "tf-idf": 0.40816326530612246
            }
        }, {
            "term": "\u010cate\u017e",
            "scores": {
            "tf": 12,
            "df": 30,
            "tf-idf": 0.4
            }
        }, {
            "term": "cigareta",
            "scores": {
            "tf": 32,
            "df": 81,
            "tf-idf": 0.3950617283950617
            }
        }, {
            "term": "progresija",
            "scores": {
            "tf": 15,
            "df": 43,
            "tf-idf": 0.3488372093023256
            }
        }, {
            "term": "neizpla\u010dan",
            "scores": {
            "tf": 28,
            "df": 82,
            "tf-idf": 0.34146341463414637
            }
        }, {
            "term": "delavski",
            "scores": {
            "tf": 197,
            "df": 582,
            "tf-idf": 0.3384879725085911
            }
        }, {
            "term": "Helios",
            "scores": {
            "tf": 38,
            "df": 116,
            "tf-idf": 0.3275862068965517
            }
        }, {
            "term": "predkupen",
            "scores": {
            "tf": 25,
            "df": 80,
            "tf-idf": 0.3125
            }
        }, {
            "term": "Telekom",
            "scores": {
            "tf": 201,
            "df": 648,
            "tf-idf": 0.3101851851851852
            }
        }, {
            "term": "Siriza",
            "scores": {
            "tf": 14,
            "df": 46,
            "tf-idf": 0.30434782608695654
            }
        }, {
            "term": "prekeren",
            "scores": {
            "tf": 33,
            "df": 109,
            "tf-idf": 0.30275229357798167
            }
        }, {
            "term": "pregrevanje",
            "scores": {
            "tf": 27,
            "df": 90,
            "tf-idf": 0.3
            }
        }, {
            "term": "klasificirati",
            "scores": {
            "tf": 25,
            "df": 84,
            "tf-idf": 0.2976190476190476
            }
        }]
    }
    """
    try:
        card = getPersonCardModelNew(Tfidf, int(person_id), date=date_, is_visible=True)
    except:
        # if perons has not card, returns empty results
        return JsonResponse({
            'person': getPersonData(person_id, date_),
            'results': [],
            "created_for": datetime.now().strftime(API_DATE_FORMAT),
            "created_at": datetime.now().strftime(API_DATE_FORMAT)
            })

    out = {
        'person': getPersonData(person_id, date_),
        'results': card.data,
        "created_for": card.created_for.strftime(API_DATE_FORMAT),
        "created_at": card.created_at.strftime(API_DATE_FORMAT)
    }

    return JsonResponse(out)


def getVocabularySize(request, person_id, date_=None):
    """
    * @api {get} /p/getVocabularySize/{id}/{?date} MP's vocabulary size
    * @apiName getVocabularySize
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated vocabulary size. The function returns the score as it was
      calculated for a given date, if no date is supplied it is assumed
      the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results MP's vocabulary size.
    * @apiSuccess {Object} results.max MP (or MPs) who has the highest vocabulary size and their score.
    * @apiSuccess {Float} results.max.score Max MP's score.
    * @apiSuccess {Object[]} results.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.max.mps.name MP's full name.
    * @apiSuccess {String} results.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.max.mps.party.name The party's name.
    * @apiSuccess {String} results.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.average The average score for this metric accross the parliament.
    * @apiSuccess {Float} results.score Score for the MP in question.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getVocabularySize/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getVocabularySize/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "14.11.2016",
        "created_for": "10.09.2014",
        "results": {
            "max": {
            "score": 744.915094339623,
            "mps": [{
                "is_active": false,
                "district": [40],
                "name": "Benedikt Kopmajer",
                "gov_id": "P261",
                "gender": "m",
                "party": {
                "acronym": "DeSUS",
                "is_coalition": true,
                "id": 3,
                "name": "PS Demokratska Stranka Upokojencev Slovenije"
                },
                "type": "mp",
                "id": 41,
                "has_function": false
            }]
            },
            "average": 388.298609949473,
            "score": 592.0
        }
    }
    """

    card = getPersonCardModelNew(VocabularySize, person_id, date_)

    out = {
        'person': getPersonData(person_id, date_),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'results': {
            'max': {
                'score': card.maximum,
                'mps': [getPersonData(card.maxMP.id_parladata, date_)]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getAverageNumberOfSpeechesPerSession(request, person_id, date=None):
    """
    * @api {get} /p/getAverageNumberOfSpeechesPerSession/{id}/{?date} MP's average number of speeches per session
    * @apiName getAverageNumberOfSpeechesPerSession
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated average number of speeches per session. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results MP's average number of speeches per session.
    * @apiSuccess {Object} results.max MP (or MPs) who has the highest speeches per session and their score.
    * @apiSuccess {Integer} results.max.score Max MP's score.
    * @apiSuccess {Object[]} results.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.max.mps.name MP's full name.
    * @apiSuccess {String} results.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.max.mps.party.name The party's name.
    * @apiSuccess {String} results.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Integer} results.average The average score for this metric accross the parliament.
    * @apiSuccess {Integer} results.score Score for the MP in question.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getAverageNumberOfSpeechesPerSession/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getAverageNumberOfSpeechesPerSession/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "02.11.2016",
        "created_for": "06.09.2014",
        "results": {
            "max": {
            "score": 31.0,
            "mps": [{
                "is_active": false,
                "district": [76],
                "name": "Milan Brglez",
                "gov_id": "P243",
                "gender": "m",
                "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
                },
                "type": "mp",
                "id": 11,
                "has_function": true
            }]
            },
            "average": 2.0,
            "score": 2.0
        }
    }
    """

    card = getPersonCardModelNew(AverageNumberOfSpeechesPerSession, person_id, date)
    #static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'results': {
            'max': {
                'score': card.maximum,
                'mps': [getPersonData(card.maxMP.id_parladata, date)]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getCompass(request, org_id, date_=None): # TODO make proper setters and getters
    """
    * @api {get} /p/getCompass/{?date} Political compass
    * @apiName getCompass
    * @apiGroup Other
    * @apiDescription This function returns a list of objects representing
      MPs and their coordinates on the "political compass". The function
      returns the scores as it was calculated for a given date, if no date
      is supplied it is assumed the date is today.
    * @apiParam {date} date Optional date.

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} data list of MPs and their coordinates

    * @apiSuccess {Object} data.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} data.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} data.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} data.person.name MP's full name.
    * @apiSuccess {String} data.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} data.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} data.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} data.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} data.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} data.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} data.person.party.name The party's name.
    * @apiSuccess {String} data.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} data.person.id The person's Parladata id.
    * @apiSuccess {Boolean} data.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSucces {Object} data.score MP's coordinates
    * @apiSuccess {Float} data.score.vT1 First coordinate
    * @apiSuccess {Float} data.score.vT2 Second coordinate


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getCompass/
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getCompass/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "created_at": "21.03.2017",
        "created_for": "17.02.2017",
        "data": [{
            "person": {
            "is_active": false,
            "district": [7],
            "name": "Anja Bah \u017dibert",
            "gov_id": "P239",
            "gender": "f",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 2,
            "has_function": false
            },
            "score": {
            "vT1": 0.18281964948320664,
            "vT2": -0.05594373814997616
            }
        }, {
            "person": {
            "is_active": false,
            "district": [8],
            "name": "Ur\u0161ka Ban",
            "gov_id": "P240",
            "gender": "f",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 3,
            "has_function": false
            },
            "score": {
            "vT1": -0.06505089721256502,
            "vT2": -0.1438729944923539
            }
        }]
    }
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=""
    try:
        compas = Compass.objects.filter(
            created_for__lte=date_of,
            organization__id_parladata=org_id
        ).order_by('-created_for')[0]
    except:
        raise Http404("Nismo našli kartice")
    data = compas.data
    for person in data:
        person.update({"person": getPersonData(person["person_id"], compas.created_for.strftime(API_DATE_FORMAT))})
        person.pop('person_id', None)

    return JsonResponse({"created_for": compas.created_for.strftime(API_DATE_FORMAT),
                         "created_at": compas.created_at.strftime(API_DATE_FORMAT),
                         "parent_org_id": int(org_id),
                         "data": data},
                        safe=False)


def getMembershipsOfMember(request, person_id, date=None): # TODO refactor keys into snake_case
    """
    * @api {get} /p/getMembershipsOfMember/{?date} MP's memberships
    * @apiName getMembershipsOfMember
    * @apiGroup MPs
    * @apiDescription This function returns an object with all the memberships the
      MP holds in various organizations. The function returns the memberships as
      they were calculated for a given date, if no date is supplied it is assumed
      the date is today.
    * @apiParam {Integer} id MP's Parladata id
    * @apiParam {date} date Optional date

    * @apiSuccess {Object} memberships MP's memberships categorised by organization type.

    * @apiSuccess {Object[]} memberships.kolegij MP's memberships in "kolegij"-type organizations.
    * @apiSuccess {String} memberships.kolegij.url Organization's url.
    * @apiSuccess {String} memberships.kolegij.org_type Organization type.
    * @apiSuccess {Integer} memberships.kolegij.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.kolegij.name The name of the organization.

    * @apiSuccess {Object[]} memberships.skupina_prijateljstva MP's memberships in "skupina prijateljstva"-type organizations.
    * @apiSuccess {String} memberships.skupina_prijateljstva.url Organization's url.
    * @apiSuccess {String} memberships.skupina_prijateljstva.org_type Organization type.
    * @apiSuccess {Integer} memberships.skupina_prijateljstva.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.skupina_prijateljstva.name The name of the organization.

    * @apiSuccess {Object[]} memberships.delegacija MP's memberships in "delegacija"-type organizations.
    * @apiSuccess {String} memberships.delegacija.url Organization's url.
    * @apiSuccess {String} memberships.delegacija.org_type Organization type.
    * @apiSuccess {Integer} memberships.delegacija.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.delegacija.name The name of the organization.

    * @apiSuccess {Object[]} memberships.komisija MP's memberships in "komisija"-type organizations.
    * @apiSuccess {String} memberships.komisija.url Organization's url.
    * @apiSuccess {String} memberships.komisija.org_type Organization type.
    * @apiSuccess {Integer} memberships.komisija.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.komisija.name The name of the organization.

    * @apiSuccess {Object[]} memberships.poslanska_skupina MP's memberships in "poslanska skupina"-type organizations.
    * @apiSuccess {String} memberships.poslanska_skupina.url Organization's url.
    * @apiSuccess {String} memberships.poslanska_skupina.org_type Organization type.
    * @apiSuccess {Integer} memberships.poslanska_skupina.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.poslanska_skupina.name The name of the organization.

    * @apiSuccess {Object[]} memberships.odbor MP's memberships in "odbor"-type organizations.
    * @apiSuccess {String} memberships.odbor.url Organization's url.
    * @apiSuccess {String} memberships.odbor.org_type Organization type.
    * @apiSuccess {Integer} memberships.odbor.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.odbor.name The name of the organization.

    * @apiSuccess {Object[]} memberships.preiskovalna_komisija MP's memberships in "preiskovalna komisija"-type organizations.
    * @apiSuccess {String} memberships.preiskovalna_komisija.url Organization's url.
    * @apiSuccess {String} memberships.preiskovalna_komisija.org_type Organization type.
    * @apiSuccess {Integer} memberships.preiskovalna_komisija.org_id Organization's Parladata id.
    * @apiSuccess {String} memberships.preiskovalna_komisija.name The name of the organization.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getMembershipsOfMember/
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getMembershipsOfMember/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "created_at": "21.03.2017",
        "created_for": "17.02.2017",
        "data": [{
            "person": {
            "is_active": false,
            "district": [7],
            "name": "Anja Bah \u017dibert",
            "gov_id": "P239",
            "gender": "f",
            "party": {
                "acronym": "SDS",
                "is_coalition": false,
                "id": 5,
                "name": "PS Slovenska Demokratska Stranka"
            },
            "type": "mp",
            "id": 2,
            "has_function": false
            },
            "score": {
            "vT1": 0.18281964948320664,
            "vT2": -0.05594373814997616
            }
        }, {
            "person": {
            "is_active": false,
            "district": [8],
            "name": "Ur\u0161ka Ban",
            "gov_id": "P240",
            "gender": "f",
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "id": 1,
                "name": "PS Stranka modernega centra"
            },
            "type": "mp",
            "id": 3,
            "has_function": false
            },
            "score": {
            "vT1": -0.06505089721256502,
            "vT2": -0.1438729944923539
            }
        }]
    }
    """
    card = getPersonCardModelNew(MembershipsOfMember, person_id, date)
    static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card.created_for.strftime(API_DATE_FORMAT),
        'memberships': card.data
    }

    return JsonResponse(out, safe=False)


def getTaggedBallots(request, person_id, date_=None):
    """
    * @api {get} /p/getTaggedBallots/{id}/{?date} MP's tagged ballots
    * @apiName getTaggedBallots
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      ballots and their tags, ordered by date, grouped by day. The function
      returns the ballots until a given date, if no date is supplied it is
      assumed the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results MP's tagged ballots grouped by date.
    * @apiSuccess {date} results.date The date in question.
    * @apiSuccess {Object[]} results.ballots Ballots the MP submitted on that day.
    * @apiSuccess {Integer} results.ballots.ballot_id Ballot's Parladata id.
    * @apiSuccess {String} results.ballots.option The ballot option ("za"/"proti"/"ni"/"kvorum").
    * @apiSuccess {String[]} results.ballots.tags List of tags this ballot was tagged with.
    * @apiSuccess {Integer} results.ballots.session_id Parladata id of the session where this ballot was submitted.
    * @apiSuccess {String} results.ballots.motion The text of the motion (what was the vote about).
    * @apiSuccess {Boolean} results.ballots.result Answers the question: Did the motion pass?
    * @apiSuccess {Integer} results.ballots.vote_id Parladata id of the vote this ballot belongs to.

    * @apiSuccess {String[]} all_tags List of all tags used for tagging ballots.


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getTaggedBallots/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getTaggedBallots/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "23. 11. 2016",
        "created_for": "4. 12. 2014",
        "results": [{
            "date": "4. 12. 2014",
            "ballots": [{
            "ballot_id": 592963,
            "option": "ni",
            "tags": ["Odbor za notranje zadeve, javno upravo in lokalno samoupravo"],
            "session_id": 5614,
            "motion": "Zakon o spremembah in dopolnitvah Zakona o dr\u017eavni upravi - Glasovanje o zakonu v celoti",
            "result": true,
            "vote_id": 6591
            }, {
            "ballot_id": 593053,
            "option": "ni",
            "tags": ["Odbor za notranje zadeve, javno upravo in lokalno samoupravo"],
            "session_id": 5614,
            "motion": "Zakon o spremembah in dopolnitvah Zakona o dr\u017eavni upravi - Amandma: K 19. \u010dlenu 4.12.2014 [ZL - Poslanska skupina Zdru\u017eena levica]",
            "result": false,
            "vote_id": 6592
            }]
        }, {
            "date": "17. 11. 2014",
            "ballots": [{
            "ballot_id": 564575,
            "option": "ni",
            "tags": ["Mandatno-volilna komisija"],
            "session_id": 6683,
            "motion": "Sklep o imenovanju \u010dlana Slovenske nacionalne komisije za UNESCO - Glasovanje",
            "result": true,
            "vote_id": 6274
            }, {
            "ballot_id": 564665,
            "option": "ni",
            "tags": ["Mandatno-volilna komisija"],
            "session_id": 6683,
            "motion": "Sklep o imenovanju predsednika in dveh \u010dlanov Upravnega odbora Sklada za financiranje razgradnje NEK in za odlaganje radioaktivnih odpadkov iz NEK - Glasovanje",
            "result": true,
            "vote_id": 6275
            }, {
            "ballot_id": 564755,
            "option": "ni",
            "tags": ["Mandatno-volilna komisija"],
            "session_id": 6683,
            "motion": "Sklep o imenovanju \u010dlanice Dr\u017eavne revizijske komisije - Glasovanje",
            "result": true,
            "vote_id": 6276
            }]
        }],
        "all_tags": ["Komisija za nadzor javnih financ", "Kolegij predsednika Dr\u017eavnega zbora", "Komisija za narodni skupnosti", "Komisija za odnose s Slovenci v zamejstvu in po svetu", "Komisija za poslovnik", "Mandatno-volilna komisija", "Odbor za delo, dru\u017eino, socialne zadeve in invalide", "Odbor za finance in monetarno politiko", "Odbor za gospodarstvo", "Odbor za infrastrukturo, okolje in prostor", "Odbor za izobra\u017eevanje, znanost, \u0161port in mladino", "Odbor za kmetijstvo, gozdarstvo in prehrano", "Odbor za kulturo", "Odbor za notranje zadeve, javno upravo in lokalno samoupravo", "Odbor za obrambo", "Odbor za pravosodje", "Odbor za zadeve Evropske unije", "Odbor za zdravstvo", "Odbor za zunanjo politiko", "Preiskovalna komisija o ugotavljanju zlorab v slovenskem ban\u010dnem sistemu ter ugotavljanju vzrokov in", "Preiskovalna komisija za ugotavljanje politi\u010dne odgovornosti nosilcev javnih funkcij pri investiciji", "Ustavna komisija", "Proceduralna glasovanja", "Zunanja imenovanja", "Poslanska vpra\u0161anja", "Komisija za nadzor obve\u0161\u010devalnih in varnostnih slu\u017eb", "Preiskovalne komisije", "Komisija za peticije ter za \u010dlovekove pravice in enake mo\u017enosti", "Interpelacija", " Preiskovalna komisija za ugotavljanje politi\u010dne odgovornosti nosilcev javnih funkcij pri investicij"]
    }
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)

    ballots = Ballot.objects.filter(person__id_parladata=person_id,
                                    start_time__lte=date_of)
    if ballots:
        created_at = ballots.latest('created_at').created_at
    else:
        created_at = datetime.now()

    b = Ballot.objects.filter(person__id_parladata=person_id,
                              start_time__lte=date_of)
    b_s = [model_to_dict(i, fields=['vote', 'option', 'id_parladata']) for i in b]
    b_s = {bal['vote']: (bal['id_parladata'], bal['option']) for bal in b_s}
    person_data = {'person': getPersonData(person_id, date_)}

    result = prepareTaggedBallots(date_of, b_s, person_data)

    return JsonResponse(result, safe=False)


def getNumberOfQuestions(request, person_id, date_=None):
    """
    * @api {get} /p/getNumberOfQuestions/{id}/{?date} MP's number of questions
    * @apiName getNumberOfQuestions
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated number of questions (like PM's questions in the UK). The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object} results MP's number of questions.
    * @apiSuccess {Object} results.max MP (or MPs) who has the highest number of questions and their score.
    * @apiSuccess {Integer} results.max.score Max MP's score.
    * @apiSuccess {Object[]} results.max.mps A list of MP's with the same maximum score.
    * @apiSuccess {Boolean} results.max.mps.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} results.max.mps.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} results.max.mps.name MP's full name.
    * @apiSuccess {String} results.max.mps.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} results.max.mps.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} results.max.mps.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} results.max.mps.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} results.max.mps.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} results.max.mps.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} results.max.mps.party.name The party's name.
    * @apiSuccess {String} results.max.mps.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Boolean} results.max.mps.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Float} results.average The average score for this metric accross the parliament.
    * @apiSuccess {Integer} results.score Score for the MP in question.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getNumberOfQuestions/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getNumberOfQuestions/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "21.03.2017",
        "created_for": "20.03.2017",
        "results": {
            "max": {
            "score": 672449,
            "mps": [{
                "is_active": false,
                "district": [17],
                "name": "Jo\u017eef Horvat",
                "gov_id": "P020",
                "gender": "m",
                "party": {
                "acronym": "NSI",
                "is_coalition": false,
                "id": 6,
                "name": "PS Nova Slovenija"
                },
                "type": "mp",
                "id": 32,
                "has_function": false
            }]
            },
            "average": 177115,
            "score": 381389
        }
    }
    """
    card = getPersonCardModelNew(NumberOfQuestions,
                                 person_id,
                                 date_)
    card_date = card.created_for.strftime(API_DATE_FORMAT)

    out = {
        'person': getPersonData(person_id, card_date),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card_date,
        'results': {
            'max': {
                'score': card.maximum,
                'mps': [getPersonData(max_p, card_date)
                        for max_p in card.maxMPs]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getQuestions(request, person_id, date_=None):
    """
    * @api {get} /p/getQuestions/{id}/{?date} MP's questions
    * @apiName getQuestions
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      questions, ordered by date, grouped by day. The function
      returns the ballots until a given date, if no date is supplied it is
      assumed the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results MP's questions grouped by date.
    * @apiSuccess {date} results.date The date in question.
    * @apiSuccess {Object[]} results.questions Questions the MP submitted on that day.
    * @apiSuccess {String} results.questions.recipient_text Recipient in text form as written on www.dz-rs.si.
    * @apiSuccess {String} results.questions.url URL to the relevant question document.
    * @apiSuccess {String} results.questions.title Question title.
    * @apiSuccess {Integer} results.questions.id Parladata id of the question.
    * @apiSuccess {Integer} results.questions.session_id Parladata id of the session where this question was asked.
    * @apiSuccess {Integer} results.questions.session_name Name of the session where this question was asked.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getQuestions/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getQuestions/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "11. 1. 2017",
        "created_for": "12. 12. 2014",
        "results": [{
            "date": "12. 12. 2014",
            "questions": [{
            "recipient_text": "minister za gospodarski razvoj in tehnologijo, ministrica za okolje in prostor",
            "title": "v zvezi s problematiko Cinkarne Celje in z njo povezanim okoljskim stanjem v Celju",
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0052d5fcd92e4bdfad7c16c7458916c91f48725827616fb01493db37336",
            "session_id": "Unknown",
            "session_name": "Unknown",
            "id": 5401
            }]
        }, {
            "date": "14. 11. 2014",
            "questions": [{
            "recipient_text": "predsednik Vlade",
            "title": "v zvezi s pripravami na privatizacijo DARS-a in strategijo upravljanja z dr\u017eavnim premo\u017eenjem",
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e00560147f954c0d998b6c8f4da8aacddff0adf58593742b0fa62dc39b11",
            "session_id": "Unknown",
            "session_name": "Unknown",
            "id": 5232
            }, {
            "recipient_text": "minister za infrastrukturo",
            "title": "v zvezi z ohranitvijo delovnih mest v Zasavju",
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e00544d15404319afbf78aa095c9c6cc3d29459887062737389aab9c7829",
            "session_id": "Unknown",
            "session_name": "Unknown",
            "id": 5234
            }]
        }, {
            "date": "29. 10. 2014",
            "questions": [{
            "recipient_text": "minister za finance v funkciji ministra za gospodarski razvoj in tehnologijo",
            "title": "z zvezi z vrnitvijo glasovalnih pravic RS in povezanih dru\u017eb v dru\u017ebah Telekom d.d. in Zavarovalnico Triglav d.d.",
            "url": "http://imss.dz-rs.si/IMiS/ImisAdmin.nsf/ImisnetAgent?OpenAgent&2&DZ-MSS-01/ca20e0052e4c3e7a939ddd5a2c137009af60900edcdabf8632dd7d796f2f8bcd",
            "session_id": 5615,
            "session_name": "6. izredna seja",
            "id": 5109
            }]
        }]
    }
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = date_of.strftime(API_DATE_FORMAT)

    end_of_day = date_of + timedelta(days=1)
    questions = Question.objects.filter(start_time__lt=end_of_day,
                                        person__id_parladata=person_id).order_by("-start_time")

    staticData = json.loads(getAllStaticData(None).content)

    personsStatic = staticData['persons']
    ministrStatic = staticData['ministrs']

    questions = questions.extra(select={'start_time_date': 'DATE(start_time)'})
    dates = list(set(list(questions.values_list("start_time_date", flat=True))))
    dates.sort()
    data = {date: [] for date in dates}

    for question in questions:
        data[question.start_time_date].append(question.getQuestionData(ministrStatic))

    out = [{'date': date.strftime(API_OUT_DATE_FORMAT),
            'questions': data[date]}
           for date in dates]

    result = {
        'results': list(reversed(out)),
        'created_for': out[-1]["date"] if out else date_,
        'created_at': out[-1]["date"] if out else date_,
        'person': getPersonData(person_id, date_),
        }
    return JsonResponse(result, safe=False)


def getAllActiveMembers(request):
    """
    * @api {get} /p/getAllActiveMembers Get all active MPs
    * @apiName getAllActiveMembers
    * @apiGroup Other
    * @apiDescription This function returns a list of all MPs currently
      active in the parliament.

    * @apiSuccess {Object[]} / list of MPs

    * @apiSuccess {Boolean} /.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} /.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} /.name MP's full name.
    * @apiSuccess {String} /.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} /.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} /.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} /.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} /.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} /.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} /.party.name The party's name.
    * @apiSuccess {String} /.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} /.id The person's Parladata id.
    * @apiSuccess {Boolean} /.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).


    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getAllActiveMembers/

    * @apiSuccessExample {json} Example response:
    [{
        "is_active": false,
        "district": [48],
        "name": "Jasna Murgel",
        "gov_id": "P274",
        "gender": "f",
        "party": {
            "acronym": "SMC",
            "is_coalition": true,
            "id": 1,
            "name": "PS Stranka modernega centra"
        },
        "type": "mp",
        "id": 60,
        "has_function": false
        }, {
        "is_active": false,
        "district": [40],
        "name": "Ivan \u0160kodnik",
        "gov_id": "P286",
        "gender": "m",
        "party": {
            "acronym": "SMC",
            "is_coalition": true,
            "id": 1,
            "name": "PS Stranka modernega centra"
        },
        "type": "mp",
        "id": 76,
        "has_function": false
        }, {
        "is_active": false,
        "district": [46],
        "name": "Branislav Raji\u0107",
        "gov_id": "P281",
        "gender": "m",
        "party": {
            "acronym": "SMC",
            "is_coalition": true,
            "id": 1,
            "name": "PS Stranka modernega centra"
        },
        "type": "mp",
        "id": 70,
        "has_function": false
    }]
    """
    return JsonResponse([getPersonData(person.id_parladata) for person in Person.objects.filter(actived="Yes")], safe=False)


def getSlugs(request):
    """
    * @api {get} /p/getSlugs Get slugs for parlameter.si
    * @apiName getAllActiveMembers
    * @apiGroup Other
    * @apiDescription This function returns slugs for our site at parlameter.si

    * @apiSuccess {Object} partyLink Party url paths.
    * @apiSuccess {String} partyLink.govori Party speeches url.
    * @apiSuccess {String} partyLink.base Party pages base url.
    * @apiSuccess {String} partyLink.pregled Party overview url.
    * @apiSuccess {String} partyLink.glasovanja Party votes url.

    * @apiSuccess {Object} personLink Person url paths.
    * @apiSuccess {String} personLink.govori Person speeches url.
    * @apiSuccess {String} personLink.base Person pages base url.
    * @apiSuccess {String} personLink.pregled Person overview url.
    * @apiSuccess {String} personLink.glasovanja Person votes url.

    * @apiSuccess {Object} sessionLink Session url paths.
    * @apiSuccess {String} sessionLink.prisotnos Session attendance url.
    * @apiSuccess {String} sessionLink.glasovanje Session vote url.
    * @apiSuccess {String} sessionLink.transkript Session transcript url.
    * @apiSuccess {String} sessionLink.glasovanja Session votes url.

    * @apiSuccess {Object} person Slugs for people. Keys are Parladata ids.
    * @apiSuccess {Object} person.PERSON_ID Person's slugs object.
    * @apiSuccess {String} person.PERSON_ID.slug Person's url slug.

    * @apiSuccess {String} base Url base.

    * @apiSuccess {Object} party Slugs for organizations. Keys are Parladata ids.
    * @apiSuccess {Object} party.PARTY_ID Party's slug object.
    * @apiSuccess {String} party.PARTY_ID.acronym Party's acronym.
    * @apiSuccess {String} party.PARTY_ID.realAcronym Party's acronym with proper capitalisation.
    * @apiSuccess {String} party.PARTY_ID.slug Party's slug

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getSlugs/

    * @apiSuccessExample {json} Example response:
    {
        "legislationLink": "/zakonodaja/",
        "partyLink": {
            "govori": "/govori/",
            "base": "/poslanska-skupina/",
            "pregled": "/pregled/",
            "glasovanja": "/glasovanja/"
        },
        "personLink": {
            "govori": "/govori/",
            "base": "/poslanec/",
            "pregled": "/pregled/",
            "glasovanja": "/glasovanja/"
        },
        "sessionLink": {
            "prisotnost": "/seja/prisotnost/",
            "glasovanje": "/seja/glasovanje/",
            "transkript": "/seja/transkript/",
            "glasovanja": "/seja/glasovanja/"
        },
        "person": {
            "2": {
            "slug": "anja-bah-zibert"
            },
            "3": {
            "slug": "urska-ban"
            },
            "4": {
            "slug": "roberto-battelli"
            }
        },
        "base": "https://parlameter.si",
        "party": {
            "1": {
            "acronym": "smc",
            "realAcronym": "SMC",
            "slug": "ps-stranka-modernega-centra"
            },
            "2": {
            "acronym": "imns",
            "realAcronym": "IMNS",
            "slug": "ps-italijanske-in-madzarske-narodne-skupnosti"
            },
            "3": {
            "acronym": "desus",
            "realAcronym": "DeSUS",
            "slug": "ps-demokratska-stranka-upokojencev-slovenije"
            },
            "4": {
            "acronym": "zaab",
            "realAcronym": "ZAAB",
            "slug": "ps-zaveznistvo-alenke-bratusek"
            }
        }
    }
    """
    obj = {"person": {person.id_parladata: {"slug": slugify(person.name)}
                      for person
                      in Person.objects.all().exclude(pg__isnull=True)},
            "personLink": {
                    "base": "/poslanec/",
                    "govori": "/govori/",
                    "glasovanja": "/glasovanja/",
                    "pregled": "/pregled/"
                },
            "party": {org.id_parladata: {"slug": slugify(org.name),
                                         "acronym": slugify(org.acronym),
                                         "realAcronym": org.acronym}
                      for org
                      in Organization.objects.all()},
            "partyLink": {
                    "base": "/poslanska-skupina/",
                    "govori": "/govori/",
                    "glasovanja": "/glasovanja/",
                    "pregled": "/pregled/"
                },

            "legislationLink": "/zakonodaja/",
            "sessionLink": {
                    "glasovanje": "/seja/glasovanje/",
                    "glasovanja": "/seja/glasovanja/",
                    "prisotnost": "/seja/prisotnost/",
                    "transkript": "/seja/transkript/"
                },
            "base": FRONT_URL,
            "urls": {
                "base": FRONT_URL,
                "analize": BASE_URL,
                "isci": ISCI_URL,
                "data": API_URL,
                "glej": GLEJ_URL,
                "notifications_api": NOTIFICATIONS_API
                }
            }
    return JsonResponse(obj)


def getPresenceThroughTime(request, person_id, date_=None):
    """
    * @api {get} /p/getPresenceThroughTime/{id}/{?date} MP's presence through time
    * @apiName getPresenceThroughTime
    * @apiGroup MPs
    * @apiDescription This function returns an object with the MPs
      calculated presence at votes through time. The function
      returns the score as it was calculated for a given date, if no date is
      supplied the date is today.
    * @apiParam {Integer} id MP's Parladata id.
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object} person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} person.name MP's full name.
    * @apiSuccess {String} person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} person.party.name The party's name.
    * @apiSuccess {String} person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} person.id The person's Parladata id.
    * @apiSuccess {Boolean} person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {date} created_at When was this data created?
    * @apiSuccess {date} created_for What historic date does this data correspond with?

    * @apiSuccess {Object[]} results List of objects for MP's presence for every month since the beginning of the current Parliament's term.
    * @apiSuccess {Integer} results.vote_count Total number of votes that happened this month.
    * @apiSuccess {date} results.date_ts UTF-8 formatted date - first of the month.
    * @apiSuccess {Integer} results.not_member Percentage of votes where this person was not yet a MP.
    * @apiSuccess {Float} results.presence Percentage of votes this person attended.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getPresenceThroughTime/12
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getPresenceThroughTime/12/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "person": {
            "is_active": false,
            "district": [15],
            "name": "Luka Mesec",
            "gov_id": "P273",
            "gender": "m",
            "party": {
            "acronym": "ZL",
            "is_coalition": false,
            "id": 8,
            "name": "PS Zdru\u017eena Levica"
            },
            "type": "mp",
            "id": 58,
            "has_function": false
        },
        "created_at": "28.02.2017",
        "created_for": "28.02.2017",
        "results": [{
            "vote_count": 17,
            "date_ts": "2014-08-01T00:00:00",
            "not_member": 0,
            "presence": 70.58823529411765
        }, {
            "vote_count": 15,
            "date_ts": "2014-09-01T00:00:00",
            "not_member": 0,
            "presence": 60.0
        }, {
            "vote_count": 4,
            "date_ts": "2014-10-01T00:00:00",
            "not_member": 0,
            "presence": 100.0
        }, {
            "vote_count": 58,
            "date_ts": "2014-11-01T00:00:00",
            "not_member": 0,
            "presence": 70.6896551724138
        }, {
            "vote_count": 61,
            "date_ts": "2014-12-01T00:00:00",
            "not_member": 0,
            "presence": 27.86885245901639
        }]
    }
    """
    card = getPersonCardModelNew(PresenceThroughTime,
                                 person_id,
                                 date_)
    card_date = card.created_for.strftime(API_DATE_FORMAT)

    out = {
        'person': getPersonData(person_id, card_date),
        'created_at': card.created_at.strftime(API_DATE_FORMAT),
        'created_for': card_date,
        'results': card.data
    }

    return JsonResponse(out, safe=False)


@lockSetter
def setListOfMembersTickers(request, org_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    # get start_time of previous session and find older card of this date

    try:
        #prev_session = Session.objects.filter(start_time__lte=date_of,
        #                                      organization__id_parladata=95,
        #                                      name__icontains=' redna')
        #session_time = prev_session.order_by("-start_time")[0].start_time


        month_ago = date_of-timedelta(days=30)
        print("mesc nazaj", month_ago)
        prevCard = getListOfMembersTickers(request, month_ago.strftime(API_DATE_FORMAT)).content
        print(json.loads(prevCard)['created_for'], json.loads(prevCard)['created_at'])
        prevData = json.loads(prevCard)['data']
    except Exception as exp:
        print exp
        prevData = []

    data = setListOfMembersTickersCore(org_id, date_, date_of, prevData)

    return JsonResponse(data, safe=False)

@lockSetter
def setListOfMembersTickersMonthly(request, org_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    # get start_time of previous session and find older card of this date

    try:
        previous_time = date_of - timedelta(days=28)

        prevCard = getListOfMembersTickers(request, org_id, previous_time.strftime(API_DATE_FORMAT)).content
        print(json.loads(prevCard)['created_for'], json.loads(prevCard)['created_at'])
        prevData = json.loads(prevCard)['data']
    except:
        prevData = []

    data = setListOfMembersTickersCore(org_id, date_, date_of, prevData)
    print(data)

    return JsonResponse(data, safe=False)

def setListOfMembersTickersCore(org_id, date_, date_of, prevData):
    print("CORE")
    mps = getVotersIDs(organization_id=org_id, date_=date_of)

    rank_data = {'presence_sessions': [],
                 'presence_votes': [],
                 'vocabulary_size': [],
                 'spoken_words': [],
                 'speeches_per_session': [],
                 'number_of_questions': [],
                 #'privzdignjeno': [],
                 #'preprosto': [],
                 #'problematicno': [],
                 'mismatch_of_pg': [],
                 }

    diffs = copy.deepcopy(rank_data)

    data = []
    for person_id in mps:
        person_obj = {}
        person_obj['results'] = {}
        person_obj['person'] = getPersonData(person_id)

        try:
            value = getPersonCardModelNew(Presence,
                                          person_id,
                                          date_).person_value_sessions
        except:
            value = 0
        person_obj['results']['presence_sessions'] = {}
        person_obj['results']['presence_sessions']['score'] = value
        rank_data['presence_sessions'].append(value)

        try:
            value = getPersonCardModelNew(Presence,
                                          person_id,
                                          date_).person_value_votes
        except:
            value = 0
        person_obj['results']['presence_votes'] = {}
        person_obj['results']['presence_votes']['score'] = value
        rank_data['presence_votes'].append(value)

        try:
            value = getPersonCardModelNew(VocabularySize,
                                          person_id,
                                          date_).score
        except:
            value = 0
        person_obj['results']['vocabulary_size'] = {}
        person_obj['results']['vocabulary_size']['score'] = value
        rank_data['vocabulary_size'].append(value)

        try:
            value = getPersonCardModelNew(SpokenWords,
                                          person_id,
                                          date_).score
        except:
            value = 0
        person_obj['results']['spoken_words'] = {}
        person_obj['results']['spoken_words']['score'] = value
        rank_data['spoken_words'].append(value)

        try:
            value = getPersonCardModelNew(AverageNumberOfSpeechesPerSession,
                                          person_id,
                                          date_).score
        except:
            value = 0
        person_obj['results']['speeches_per_session'] = {}
        person_obj['results']['speeches_per_session']['score'] = value
        rank_data['speeches_per_session'].append(value)

        try:
            value = getPersonCardModelNew(NumberOfQuestions,
                                          person_id,
                                          date_).score
        except:
            value = 0
        person_obj['results']['number_of_questions'] = {}
        person_obj['results']['number_of_questions']['score'] = value
        rank_data['number_of_questions'].append(value)

        try:
            mpStatic = getPersonCardModelNew(MPStaticPL,
                                             int(person_id))
            mandates = mpStatic.mandates
            education = mpStatic.education_level
            gender = mpStatic.gender
            birth_date = mpStatic.birth_date
        except:
            mandates = None
            education = None
            gender = None
            birth_date = None

        person_obj['results']['birth_date'] = {}
        person_obj['results']['birth_date']['score'] = birth_date
        person_obj['results']['mandates'] = {}
        person_obj['results']['mandates']['score'] = mandates
        person_obj['results']['education'] = {}
        person_obj['results']['education']['score'] = education
        person_obj['results']['gender'] = {}
        person_obj['results']['gender']['score'] = gender


        """try:
            styleScores = getPersonCardModelNew(StyleScores,
                                                int(person_id),
                                                date_)
        except:
            styleScores = None

        privzdignjeno = 0
        problematicno = 0
        preprosto = 0
        try:
            if (styleScores.privzdignjeno != 0 and
               styleScores.privzdignjeno_average != 0):
                privzdignjeno = styleScores.privzdignjeno / styleScores.privzdignjeno_average

            if (styleScores.problematicno != 0 and
               styleScores.problematicno_average != 0):
                problematicno = styleScores.problematicno / styleScores.problematicno_average

            if (styleScores.preprosto != 0 and
               styleScores.preprosto_average != 0):
                preprosto = styleScores.preprosto / styleScores.preprosto_average
        except:
            preprosto = 0
            privzdignjeno = 0
            problematicno = 0"""

        try:
            mismatch = getPersonCardModelNew(MismatchOfPG,
                                              int(person_id),
                                              date_).data
        except:
            mismatch = 0
        person_obj['results']['mismatch_of_pg'] = {}
        person_obj['results']['mismatch_of_pg']['score'] = mismatch
        rank_data['mismatch_of_pg'].append(value)

        """person_obj['results']['privzdignjeno'] = {}
        person_obj['results']['privzdignjeno']['score'] = privzdignjeno
        rank_data['privzdignjeno'].append(value)

        person_obj['results']['preprosto'] = {}
        person_obj['results']['preprosto']['score'] = preprosto
        rank_data['preprosto'].append(value)

        person_obj['results']['problematicno'] = {}
        person_obj['results']['problematicno']['score'] = problematicno
        rank_data['problematicno'].append(value)"""

        data.append(person_obj)

    ranking = {}
    for key in rank_data.keys():
        ranks = rank_data[key]
        inverse = len(ranks) + 1
        ranking[key] = inverse - rankdata(ranks, method='max').astype(int)


    # set rankings to persons data
    for idx, cPerson in enumerate(data):
        # get persons data in previous list
        is_prev = True
        if prevData:
            prevPerson = prevData[idx]
            if prevPerson['person']['id'] == cPerson['person']['id']:
                pass
            else:
                # if person isn't in the same place in the list
                prevPerson = None
                for person in prevData:
                    if person['person']['id'] == cPerson['person']['id']:
                        prevPerson = person
                        continue
                # if person isn't member in the previous list
                if not prevPerson:
                    is_prev = False
        else:
            is_prev = False
        for key in rank_data.keys():
            cPerson['results'][key]['rank'] = ranking[key][idx]
            if is_prev:
                if key in prevPerson['results'].keys():
                    prevSocre = prevPerson['results'][key]['score']
                    currentScore = cPerson['results'][key]['score']
                    try:
                        diff = currentScore - prevSocre
                    except:
                        diff = 0
                    diffs[key].append(abs(diff))
                    cPerson['results'][key]['diff'] = diff

                else:
                    cPerson['results'][key]['diff'] = 0
            else:
                cPerson['results'][key]['diff'] = 0

    # check if some card haven't new data
    key_without_data = []
    for key, diff in diffs.items():
        if not sum(diff):
            print key, sum(diff)
            key_without_data.append(key)
    print prevData
    # TODO BRING THIS BACK
    # if key_without_data and prevData:
    #     return {'status': 'failed', 'cards_without_new_data': key_without_data}

    # if key_without_data:
    #     return {'status': 'failed', 'cards_without_new_data': key_without_data}

    data = sorted(data, key=lambda k: k['person']['name'])

    MembersList(created_for=date_of,
                organization=Organization.objects.get(id_parladata=org_id),
                data=data).save()
    return data


def getListOfMembersTickers(request, org_id, date_=None):
    """
    * @api {get} /p/getListOfMembersTickers/{?date} List of MPs and their scores with differences from last regular plenary session
    * @apiName getListOfMembersTickers
    * @apiGroup Other
    * @apiDescription This function returns an object with all MPs and their
      scores for all analyses along with an object containing all districts
      (for filtering purposes https://parlameter.si/poslanci). The score objects
      contain scores, MP's ranks as well as the difference in their scores between
      the last two regular plenary session (Redna seja).
    * @apiParam {date} date Optional date.

    * @apiSuccess {Object[]} districts List of objects representing districts.
    * @apiSuccess {String} districts.DISTRICT_ID Each object contains a single key,
      that key being the district's Parladata id and its value the district's name.
    * @apiSuccess {Object[]} data List of MPs and their scores.
    * @apiSuccess {Object} data.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} data.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} data.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} data.person.name MP's full name.
    * @apiSuccess {String} data.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} data.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} data.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} data.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} data.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} data.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} data.person.party.name The party's name.
    * @apiSuccess {String} data.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} data.person.id The person's Parladata id.
    * @apiSuccess {Boolean} data.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    * @apiSuccess {Object} data.results Analysis results for this person.

    * @apiSuccess {Object} data.results.privzdignjeno "Elevated" language style score object.
    * @apiSuccess {Float} data.results.privzdignjeno.diff "Elevated" language style score difference.
    * @apiSuccess {Float} data.results.privzdignjeno.score "Elevated" language style score.
    * @apiSuccess {Integer} data.results.privzdignjeno.rank "Elevated" language style score rank.

    * @apiSuccess {Object} data.results.speeches_per_session Average number of speeches per session object.
    * @apiSuccess {Float} data.results.speeches_per_session.diff Average number of speeches per session difference.
    * @apiSuccess {Float} data.results.speeches_per_session.score Average number of speeches per session.
    * @apiSuccess {Integer} data.results.speeches_per_session.rank Average number of speeches per session rank.

    * @apiSuccess {Object} data.results.number_of_questions Number of questions this MP has asked object.
    * @apiSuccess {Integer} data.results.number_of_questions.diff Number of questions this MP has asked difference.
    * @apiSuccess {Integer} data.results.number_of_questions.score Number of questions this MP has asked.
    * @apiSuccess {Integer} data.results.number_of_questions.rank Number of questions this MP has asked rank.

    * @apiSuccess {Object} data.results.presence_votes Percentage of votes this MP attended object.
    * @apiSuccess {Float} data.results.presence_votes.diff Percentage of votes this MP attended difference.
    * @apiSuccess {Float} data.results.presence_votes.score Percentage of votes this MP attended.
    * @apiSuccess {Integer} data.results.presence_votes.rank Percentage of votes this MP attended rank.

    * @apiSuccess {Object} data.results.presence_sessions Percentage of sessions this MP attended object.
    * @apiSuccess {Float} data.results.presence_sessions.diff Percentage of sessions this MP attended difference.
    * @apiSuccess {Float} data.results.presence_sessions.score Percentage of sessions this MP attended.
    * @apiSuccess {Integer} data.results.presence_sessions.rank Percentage of sessions this MP attended rank.

    * @apiSuccess {Object} data.results.problematicno "Problematic" language style score object.
    * @apiSuccess {Float} data.results.problematicno.diff "Problematic" language style score difference.
    * @apiSuccess {Float} data.results.problematicno.score "Problematic" language style score.
    * @apiSuccess {Integer} data.results.problematicno.rank "Problematic" language style score rank.

    * @apiSuccess {Object} data.results.vocabulary_size MP's calculated vocabulary size object.
    * @apiSuccess {Integer} data.results.vocabulary_size.diff MP's calculated vocabulary size difference.
    * @apiSuccess {Integer} data.results.vocabulary_size.score MP's calculated vocabulary size.
    * @apiSuccess {Integer} data.results.vocabulary_size.rank MP's calculated vocabulary size rank.

    * @apiSuccess {Object} data.results.spoken_words Number of words this MP has spoken.
    * @apiSuccess {Integer} data.results.spoken_words.diff Number of words this MP has spoken difference.
    * @apiSuccess {Integer} data.results.spoken_words.score Number of words this MP has spoken.
    * @apiSuccess {Integer} data.results.spoken_words.rank Number of words this MP has spoken rank.

    * @apiSuccess {Object} data.results.preprosto "Simple" language style score object.
    * @apiSuccess {Float} data.results.preprosto.diff "Simple" language style score difference.
    * @apiSuccess {Float} data.results.preprosto.score "Simple" language style score.
    * @apiSuccess {Integer} data.results.preprosto.rank "Simple" language style score rank.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/p/getListOfMembersTickers
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/p/getListOfMembersTickers/12.12.2016

    * @apiSuccessExample {json} Example response:
    {
        "districts": [{
            "91": "Lendava 1"
        }, {
            "102": "Ljubljana-\u0160i\u0161ka I"
        }, {
            "101": "Ljubljana-\u0160i\u0161ka II"
        }, {
            "100": "Ljubljana-\u0160i\u0161ka III"
        }, {
            "99": "Ljubljana-\u0160i\u0161ka IV"
        }],
        "created_at": "2017-03-21T10:35:29.257",
        "created_for": "2017-03-21",
        "data": [{
            "person": {
            "name": "Aleksander Kav\u010di\u010d",
            "gov_id": "P259",
            "gender": "m",
            "is_active": false,
            "district": [19],
            "party": {
                "acronym": "SMC",
                "is_coalition": true,
                "name": "PS Stranka modernega centra",
                "id": 1
            },
            "type": "mp",
            "id": 39,
            "has_function": false
            },
            "results": {
            "privzdignjeno": {
                "diff": -0.07080984812327795,
                "score": 2.7438091511157987,
                "rank": 62
            },
            "speeches_per_session": {
                "diff": 0.0,
                "score": 1.0,
                "rank": 74
            },
            "number_of_questions": {
                "diff": 0.0,
                "score": 5.0,
                "rank": 62
            },
            "presence_votes": {
                "diff": 0.0681428694927888,
                "score": 89.589905362776,
                "rank": 37
            },
            "presence_sessions": {
                "diff": -1.1897036556349008,
                "score": 89.8550724637681,
                "rank": 42
            },
            "problematicno": {
                "diff": 0.04653717835381821,
                "score": 2.516673651070962,
                "rank": 62
            },
            "vocabulary_size": {
                "diff": 0.0,
                "score": 135.0,
                "rank": 14
            },
            "spoken_words": {
                "diff": 0,
                "score": 10837,
                "rank": 86
            },
            "preprosto": {
                "diff": 0.016475585916483126,
                "score": 3.377309423797745,
                "rank": 62
            }
            }
        }, {
            "person": {
            "name": "Alenka Bratu\u0161ek",
            "gov_id": "P166",
            "gender": "f",
            "is_active": false,
            "district": [62],
            "party": {
                "acronym": "PS NP",
                "is_coalition": false,
                "name": "PS nepovezanih poslancev ",
                "id": 109
            },
            "type": "mp",
            "id": 9,
            "has_function": false
            },
            "results": {
            "privzdignjeno": {
                "diff": 0.0022796756059407786,
                "score": 0.32064092814348816,
                "rank": 26
            },
            "speeches_per_session": {
                "diff": 0.0,
                "score": 5.0,
                "rank": 26
            },
            "number_of_questions": {
                "diff": 6.0,
                "score": 49.0,
                "rank": 26
            },
            "presence_votes": {
                "diff": -1.0823189594820946,
                "score": 46.6876971608833,
                "rank": 88
            },
            "presence_sessions": {
                "diff": 0.8219770711659038,
                "score": 72.463768115942,
                "rank": 87
            },
            "problematicno": {
                "diff": 0.005426527504002687,
                "score": 0.31498556069390254,
                "rank": 26
            },
            "vocabulary_size": {
                "diff": 0.0,
                "score": 96.0,
                "rank": 72
            },
            "spoken_words": {
                "diff": 2326,
                "score": 282204,
                "rank": 19
            },
            "preprosto": {
                "diff": 0.0014815186579075212,
                "score": 0.411863764711025,
                "rank": 26
            }
            }
        }]
    }
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    lists = MembersList.objects.filter(organization__id_parladata=org_id, created_for__lte=date_of)
    if not lists:
        return JsonResponse({'created_at': date_,
                             'created_for': date_,
                             'data': [],
                             'parent_org_id': int(org_id),
                             'districts': [{dist.id_parladata: dist.name}
                                       for dist in District.objects.all()]},
                            safe=False)
    last_day = lists.latest('created_for').created_for
    cards = MembersList.objects.filter(organization__id_parladata=org_id, created_for=last_day)
    card = cards.latest('created_at')
    districts_ids =  [d for obj in card.data
                        if obj['person']['district']
                        for d in obj['person']['district']]
    return JsonResponse({'created_at': card.created_at,
                         'created_for': card.created_for,
                         'data': card.data,
                         'parent_org_id': int(org_id),
                         'districts': [{dist.id_parladata: dist.name}
                                       for dist in District.objects.filter(id_parladata__in=districts_ids)]},
                        safe=False)


def getMismatchWithPG(request, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    mismatch = getPersonCardModelNew(MismatchOfPG, int(person_id), date_)

    data = {'person': getPersonData(person_id),
            'created_at': mismatch.created_at.strftime(API_DATE_FORMAT),
            'created_for': mismatch.created_for.strftime(API_DATE_FORMAT),
            'result': {
                'score': mismatch.data,
                'max': {
                    'mps': [getPersonData(mismatch.maxMP.id_parladata, date_)],
                    'score': mismatch.maximum
                    },
                'average': mismatch.average
                }
            }
    return JsonResponse(data)


def getNumberOfAmendmetsOfMember(request, person_id, date_=None):
    """
    * @api {get} getNumberOfAmendmetsOfMember/{pg_id}/{?date} Gets number of amendments of specific organization
    * @apiName getNumberOfAmendmetsOfMember
    * @apiGroup MPs
    * @apiDescription This function returns number of amendments of specific member
    * @apiParam {Integer} person_id Parladata id for the member in question.
    * @apiParam {date} date Optional date.

    * @apiExample {curl} Example:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfAmendmetsOfMember/1
    * @apiExample {curl} Example with date:
        curl -i https://analize.parlameter.si/v1/pg/getNumberOfAmendmetsOfMember/1/12.12.2015
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date() + timedelta(days=1)
        date_ = ''
    members = getVotersIDs(date_=date_of)
    person = count = last_card_date = None
    data = []
    for p_id in members:
        temp_person, temp_count, last_card = getPersonAmendmentsCount(p_id, date_of)
        data.append({'value': temp_count,
                     'person_obj': temp_person,
                     'party_id': person_id})
        if str(p_id) == str(person_id):
            print("FOUND")
            person = temp_person
            count = temp_count
            last_card_date = last_card

    maxAmendmets = max(data, key=lambda x:x['value'] if x['value'] else 0)

    values = [i['value'] for i in data if i['value']]
    if values:
        avg = float(sum(values))/len(values)
    else:
        avg = 0

    out = {'person': getPersonData(person.id_parladata),
           'created_at': datetime.now().strftime(API_DATE_FORMAT),
           'created_for': last_card_date.strftime(API_DATE_FORMAT),
           'result': {
               'score': count,
               'max': {
                   'pgs': [getPersonData(maxAmendmets['person_obj'].id_parladata, date_) if maxAmendmets['person_obj'] else {}],
                   'score': maxAmendmets['value']
                   },
               'average': avg
               }
            }
    return JsonResponse(out, safe=False)
