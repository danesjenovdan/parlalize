from django.conf import settings

from parlalize.utils_ import getDataFromPagerApiDRFGen
from parlaskupine.models import Organization

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

def getParentOrganizationsWithVoters():
    return Organization.objects.filter(has_voters=True).values_list('id_parladata', flat=True)