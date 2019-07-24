from django.conf import settings

from parlalize.utils_ import getDataFromPagerApiDRFGen, tryHard
from parlaskupine.models import Organization
from parlaseje.models import Ballot

from datetime import datetime
from collections import defaultdict

import requests


def getVotersIDs(date_=datetime.now(), organization_id=None,):
    voters_url = settings.API_URL + '/memberships/?role=voter'
    voters_ids = []
    for voters in getDataFromPagerApiDRFGen(voters_url):
        for voter in voters:
            if organization_id:
                # skip person if is not voter of required organization
                if voter['organization'] != organization_id:
                    continue
            # check if person is voter on required date
            if voter['start_time'] < date_.isoformat():
                if voter['end_time'] == None or voter['end_time'] > date_.isoformat():
                    voters_ids.append(voter['person'])
    return voters_ids

def getOrganizationsWithVoters(date_=datetime.now(), organization_id=None):
    voters_url = settings.API_URL + '/memberships/?role=voter'
    organization_ids = []
    for voters in getDataFromPagerApiDRFGen(voters_url):
        for voter in voters:
            if organization_id:
                # skip person if is not voter of required organization
                if voter['organization'] != organization_id:
                    continue
            if voter['start_time'] < date_.isoformat():
                if voter['end_time'] == None or voter['end_time'] > date_.isoformat():
                    organization_ids.append(voter['on_behalf_of'])

    return list(set(organization_ids))

def getVotersPairsWithOrg(date_=datetime.now(), organization_id=None):
    voters_url = settings.API_URL + '/memberships/?role=voter'
    voters_ids = {}
    for voters in getDataFromPagerApiDRFGen(voters_url):
        for voter in voters:
            if organization_id:
                # skip person if is not voter of required organization
                if voter['organization'] != int(organization_id):
                    continue
            # check if person is voter on required date
            if voter['start_time'] < date_.isoformat():
                if voter['end_time'] == None or voter['end_time'] > date_.isoformat():
                    voters_ids[voter['person']] = voter['on_behalf_of']
    return voters_ids

def getOrganizationsWithVotersList(date_=datetime.now(), organization_id=None):
    voters = getVotersPairsWithOrg(date_=date_, organization_id=organization_id)
    reversed_dict = defaultdict(list)
    for key, value in voters.items():
        reversed_dict[value].append(key)
    return dict(reversed_dict)

def getLinks(*args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    links_url = settings.API_URL + '/links/'
    if query_url:
        links_url = links_url + '?' + query_url
    out = []
    for urls in getDataFromPagerApiDRFGen(links_url):
        out += urls

    return out

def getQuestions(*args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    questions_url = settings.API_URL + '/questions/'
    if query_url:
        questions_url = questions_url + '?' + query_url
    out = []
    for urls in getDataFromPagerApiDRFGen(questions_url):
        out += urls

    return out

def getMemberships(*args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    memberships_url = settings.API_URL + '/memberships/'
    if query_url:
        memberships_url = memberships_url + '?' + query_url
    out = []
    for urls in getDataFromPagerApiDRFGen(memberships_url):
        out += urls

    return out

def getPosts(date_=datetime.now(), *args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    posts_url = settings.API_URL + '/posts/'
    if query_url:
        posts_url = posts_url + '?' + query_url
    out = []
    for posts in getDataFromPagerApiDRFGen(posts_url):
        for post in posts:
            if post['start_time'] < date_.isoformat():
                if post['end_time'] == None or post['end_time'] > date_.isoformat():
                    out.append(post)
    return out

def getContactDetails(*args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    contact_detail_url = settings.API_URL + '/contact_detail/'
    if query_url:
        contact_detail_url = contact_detail_url + '?' + query_url
    out = []
    for urls in getDataFromPagerApiDRFGen(contact_detail_url):
        out += urls

    return out

def getMembershipsOfMember(person_id=None, date_=datetime.now()):
    url = settings.API_URL + '/memberships/'
    if person_id:
        url += '?person='+str(person_id)
    out_data = []
    for memberships in getDataFromPagerApiDRFGen(url):
        for membership in memberships:
            if membership['start_time'] < date_.isoformat():
                if membership['end_time'] == None or membership['end_time'] > date_.isoformat():
                    out_data.append(membership)
    return out_data

def getOrganizations(id_=None):
    url = settings.API_URL + '/organizations/'
    if id_:
        return requests.get(url + str(id_)).json()
    else:
        return [
            organization
            for organizations in getDataFromPagerApiDRFGen(url)
            for organization in organizations]

def getBallotsOfVote(vote_id):
    url = settings.API_URL + '/ballots/?vote=' + str(vote_id)
    out_data = []
    for ballots in getDataFromPagerApiDRFGen(url):
        out_data += ballots

    return out_data

def getBallotsForSession(session_id):
    url = settings.API_URL + '/ballots/?vote__session=' + str(session_id)
    out_data = []
    for ballots in getDataFromPagerApiDRFGen(url):
        out_data += ballots

    return out_data

def getVotesForSession(session_id):
    url = settings.API_URL + '/votes/?session=' + str(session_id)
    out_data = []
    for votes in getDataFromPagerApiDRFGen(url):
        out_data += votes

    return out_data

def getMotion(motion_id):
    url = settings.API_URL + '/motions/' + str(motion_id)
    out_data = tryHard(url)

    return out_data.json()

def getSessions(*args, **kwargs):
    query_url = '&'.join([str(i) +'=' + str(j) for i, j in kwargs.items()])
    sessions_url = settings.API_URL + '/sessions/'
    if query_url:
        sessions_url = sessions_url + '?' + query_url
    out = []
    for urls in getDataFromPagerApiDRFGen(sessions_url):
        out += urls
    return out

def getAllPGs(parent_org=None):
    orgs = getOrganizationsWithVoters(organization_id=parent_org)
    url = settings.API_URL + '/organizations/?ids=' + ','.join(map(str, orgs))
    out = {}
    for orgs in getDataFromPagerApiDRFGen(url):
        for org in orgs:
            out[org['id']] = org
    return out

def getCoalitionPGs(parent_org=None):
    orgs = getOrganizationsWithVoters(organization_id=parent_org)
    url = settings.API_URL + '/organizations/?ids=' + ','.join(map(str, orgs))
    out_data = {
        'coalition': [],
        'opposition': []
    }
    for orgs in getDataFromPagerApiDRFGen(url):
        for org in orgs:
            if org['is_coalition']:
                out_data['coalition'].append(org['id'])
            else:
                out_data['opposition'].append(org['id'])
    return out_data

# Move this to other place

def getParentOrganizationsWithVoters():
    return Organization.objects.filter(has_voters=True).values_list('id_parladata', flat=True)


def getNumberOfAllMPAttendedSessions(date_, members_ids):
    data = {"sessions": {}, "votes": {}}
    for member in members_ids:

        # list of all sessions of MP
        allOfHimS = list(set(Ballot.objects.filter(person__id_parladata=member,
                                                    vote__start_time__lte=date_).values_list("vote__session", flat=True)))
        # list of all session that the opiton of Ballot was: kvorum, proti, za
        votesOnS = list(set(Ballot.objects.filter(Q(option="abstain") |
                                                    Q(option="against") |
                                                    Q(option="for"),
                                                    person__id_parladata=member,
                                                    vote__start_time__lte=date_).values_list("vote__session", flat=True)))
        # list of all votes of MP
        allOfHimV = list(set(Ballot.objects.filter(person__id_parladata=member,
                                                    vote__start_time__lte=date_).values_list("vote", flat=True)))
        # list of all votes that the opiton of ballot was: kvorum, proti, za
        votesOnV = list(set(Ballot.objects.filter(Q(option="abstain") |
                                                    Q(option="against") |
                                                    Q(option="for"),
                                                    person__id_parladata=member,
                                                    vote__start_time__lte=date_).values_list("vote", flat=True)))
        try:
            data["sessions"][member] = float(len(votesOnS)) / float(len(allOfHimS)) * 100
            data["votes"][member] = float(len(votesOnV)) / float(len(allOfHimV)) * 100
        except:
            print member.id, " has no votes in this day"
    return data
