import pandas as pd
import csv
import json
import requests
from datetime import datetime
import itertools
from collections import Counter
from parlaposlanci.models import MismatchOfPG, Person
from parlaskupine.models import Organization
from parlalize.utils import saveOrAbortNew

def set_mismatch_of_pg():
    print 'prepare date'
    date_ = ''
    API_URL = 'https://data.parlameter.si/v1'
    url = API_URL + '/getVotesTableExtended'
    data = pd.read_json(url)
    url = API_URL + '/getMPs/' + date_
    mps = requests.get(url).json()
    members = [mp['id'] for mp in mps]
    url = API_URL + '/getMembersOfPGsOnDate/' + date_
    memsOfPGs = requests.get(url).json()
    url = API_URL + '/getAllPGs/' + date_
    pgs = requests.get(url).json()

    coalition = requests.get(API_URL + '/getCoalitionPGs').json()['coalition']
    orgs = requests.get(API_URL + '/getAllPGsExt/')
    data['option_ni'] = 0
    data['option_za'] = 0
    data['option_proti'] = 0
    data['option_kvorum'] = 0
    data.loc[data['option'] == 'ni', 'option_ni'] = 1
    data.loc[data['option'] == 'za', 'option_za'] = 1
    data.loc[data['option'] == 'proti', 'option_proti'] = 1
    data.loc[data['option'] == 'kvorum', 'option_kvorum'] = 1
    data['voter_unit'] = 1
    data['is_coalition'] = 0
    data.loc[data['voterparty'].isin(coalition), 'is_coalition'] = 1

    print 'start analyze'

    #za proti ni kvorum
    all_votes = data.groupby('vote_id').sum()
    m_to_p = {i['id']: i['party_id'] for i in mps}
    mppgs = pd.DataFrame(m_to_p.items(), columns=['voter', 'voterparty'])

    #Get ballots of last members party
    keys = ['voter', 'voterparty']
    i1 = mppgs.set_index(keys).index
    i2 = data.set_index(keys).index
    data2 = data[i2.isin(i1)]

    mps[0]['acronym']
    def getPartyBallot(row):
        """
        using for set ballot of party:

        methodology: ignore not_present
        """
        stats = {'za': row['option_za'],
                 'proti': row['option_proti'],
                 'kvorum': row['option_kvorum']}
                 #'ni': row['option_ni']}
        if max(stats.values()) == 0:
            return None
        max_ids = [key for key, val in stats.iteritems() if val == max(stats.values())]
        #if len(max_ids) > 1:
        #    return None
        #return max_ids[0]
        return ','.join(max_ids)

    partyBallots = data.groupby(['vote_id',
                                 'voterparty']).sum().apply(lambda row: getPartyBallot(row), axis=1)
    partys = partyBallots.reset_index()
    partys = partys.rename(columns = {0:'partyoption'})

    result = pd.merge(data2, partys, on=['vote_id', 'voterparty'])
    #remove ni option
    result = result[result.option != 'ni']

    members_vote_count = result[['voter','voter_unit']].groupby('voter').count()

    def is_equal(row):
        if row['partyoption'] and row['option'] in row['partyoption']:
            return 1
        else:
            return 2

    #equal_indexes = result[['option', 'partyoption']].apply(pd.Series.nunique, axis=1).reindex()
    equal_indexes = result[['option', 'partyoption']].apply(lambda x: is_equal(x), axis=1).reindex()
    result['ivan'] = result[['option', 'partyoption']].apply(lambda x: is_equal(x), axis=1).reindex()

    out = pd.concat([result, equal_indexes], axis=1).rename(columns = {0: 'equal_vote'})
    out = out[out['equal_vote']==1]

    members_equal_count = out[['voter', 'equal_vote']].groupby('voter').sum()

    final = pd.concat([members_equal_count, members_vote_count], axis=1)

    final['percent'] = final.apply(lambda x: float(x['equal_vote'])/x['voter_unit']*100.0, axis=1)
    print 'saveing'
    print final.index.values
    for member, row in final.iterrows():
        print member
        value = 100 - row['percent']
        person = Person.objects.get(id_parladata=member)
        party_id = person.static_data.latest('created_at').party_id
        party_classification = Organization.objects.get(id_parladata=party_id).classification
        if party_classification != 'poslanska skupina':
            value = None
        saveOrAbortNew(model=MismatchOfPG,
                       person=person,
                       created_for=datetime.now(),
                       data=value)