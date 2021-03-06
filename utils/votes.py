import csv
import pandas as pd
import json

from datetime import datetime

from parlalize.settings import API_URL, API_DATE_FORMAT, VOTE_MAP
from parlalize.utils_ import tryHard, saveOrAbortNew, getDataFromPagerApi, getDataFromPagerApiGen

from utils.parladata_api import getVotersIDs, getOrganizationsWithVotersList, getParentOrganizationsWithVoters, getBallotTable, getOrganizationsWithVoters

from parlaseje.models import Session
from parlaposlanci.models import Person, EqualVoters, LessEqualVoters, Presence
from parlaskupine.models import (Organization, MostMatchingThem,
                                 LessMatchingThem, DeviationInOrganization,
                                 PercentOFAttendedSession)


class VotesAnalysis(object):
    def __init__(self, organization_id, date_=None):
        self.debug = False
        if date_:
            self.date_ = date_.strftime(API_DATE_FORMAT)
            self.date_of = date_
        else:
            self.date_ = ''
            self.date_of = datetime.now()
        self.api_url = None
        self.members = None
        self.data = None
        self.organization_id = organization_id

        self.presenceOfPGsSignleSessions = None
        self.presenceMP_S = None
        self.presenceMP_V = None
        self.equalVotersData = None
        self.equalVotersPGData = None
        self.memsOfPGs = None
        self.presencePGs = None
        self.pgs = None

        print 'getData'
        self.prepareData()

        # analyse
        print 'analyse'
        self.presenceMPsSessions()
        self.presenceMPsVotes()
        self.presencePGsTogether()
        self.equalVoters()
        self.equalVotersPG()

    def prepareData(self):
        if self.debug:
            self.data = pd.read_pickle('backup_baze.pkl')
        else:
            self.data = pd.DataFrame()
            for page in getBallotTable(organization=self.organization_id):
                temp = pd.DataFrame(page)
                self.data = self.data.append(temp, ignore_index=True)

        self.members = getVotersIDs(organization_id=self.organization_id, date_=self.date_of)
        self.memsOfPGs = getOrganizationsWithVotersList(organization_id=self.organization_id, date_=self.date_of)
        self.pgs = getOrganizationsWithVoters(organization_id=self.organization_id, date_=self.date_of)

        def toLogic(row):
            """
            voter option to logic value
            """
            return VOTE_MAP[row['option']]

        # prepere helper columns (logic, option_ni, voter_unit)
        self.data['logic'] = self.data.apply(lambda row: toLogic(row), axis=1)
        self.data['option_x'] = 0
        self.data.loc[self.data['option'] == 'absent', 'option_x'] = 1
        self.data['voter_unit'] = 1

    # analyses
    def presencePGsSingleSessions(self):
        """
        Analyse presence of partys on single sessions
        """
        data2 = self.data.groupby(['voterparty',
                                   'session_id'],).sum().reset_index()
        data2['attendance'] = 100 * (1 - data2.option_x / data2.voter_unit)
        self.presenceOfPGsSignleSessions = data2

    def presenceMPsSessions(self):
        """
        Analyse members presence on sessions
        """
        data2 = self.data.groupby(['voter', 'session_id']).sum().reset_index()
        data2['attendance'] = 1 - data2.option_x / data2.voter_unit
        nonAttendanceCount = data2[data2.attendance == 0.0].groupby(['voter'])
        nonAttendanceCount = nonAttendanceCount.count().id.reset_index()
        allSessionsCount = data2.groupby(['voter']).count().id.reset_index()
        out = pd.merge(nonAttendanceCount,
                       allSessionsCount,
                       on='voter',
                       how='right')
        out = out.fillna(0)
        out['attendance'] = 100 * (1 - out.id_x / out.id_y)
        self.presenceMP_S = out

    def presenceMPsVotes(self):
        """
        Analyse members presence on votes
        """
        data2 = self.data.groupby(['voter']).sum().reset_index()
        data2['attendance'] = 100 * (1 - data2.option_x / data2.voter_unit)
        out = data2[['voter', 'attendance']]
        self.presenceMP_V = out

    def presencePGsTogether(self):
        """
        Analyse partys presence on sessions and votes
        get average score of members in party
        """
        pSes = self.presenceMP_S
        pVote = self.presenceMP_V
        pg_mps = self.memsOfPGs
        pgs = [key for key, value in pg_mps.items() if value]
        sessions = [pSes[pSes.voter.isin(pg_mps[pg])].mean().attendance
                    for pg
                    in pgs]

        votes = [pVote[pVote.voter.isin(pg_mps[pg])].mean().attendance
                 for pg
                 in pgs]
        d = {'pg': pd.Series(pgs, index=pgs),
             'votes': pd.Series(votes, index=pgs),
             'sessions': pd.Series(sessions, index=pgs)}
        self.presencePGs = pd.DataFrame(d)

    def equalVoters(self):
        """
        Analyse how equal are voters
        """
        data2 = self.data[['voter',
                           'vote',
                           'logic']].pivot('voter', 'vote')
        data2 = data2.transpose().reset_index().iloc[:, 2:]
        zero_data = data2.fillna(0)
        distance = lambda column1, column2: pd.np.linalg.norm(column1 - column2)
        result = zero_data.apply(lambda col1: zero_data.apply(lambda col2: distance(col1, col2)))
        self.equalVotersData = result

    def equalVotersPG(self):
        """
        Analyse how equal are voters to partys and deviation in party
        """
        averagePGs = self.data[['voterparty',
                                'vote',
                                'logic']].groupby(['voterparty',
                                                   'vote']).mean()
        averagePGs = averagePGs.reset_index().pivot('voterparty',
                                                    'vote').transpose()
        membersLogis = self.data[['voter',
                                  'vote',
                                  'logic']].pivot('voter',
                                                  'vote').transpose()

        zero_data_pg = averagePGs.fillna(0)
        zero_data_mp = membersLogis.fillna(0)
        distance = lambda column1, column2: pd.np.linalg.norm(column1 - column2)
        result = zero_data_pg.apply(lambda col1: zero_data_mp.apply(lambda col2: distance(col1, col2)))
        self.equalVotersPGData = result

    # setters
    def setEqualVoters(self):
        """
        set cards how equal are voters
        """
        for mp in self.members:
            print '.:' + str(mp) + ':.'
            person = Person.objects.get(id_parladata=int(mp))
            try:
                r = self.equalVotersData[mp]
            except:
                print mp, 'fail set equal voters'
                continue
            mps_data = r.reset_index().sort_values(mp, ascending=False)

            # most equal
            most_data = []
            data = mps_data
            for idx in range(len(data)-1):
                member_id = int(data.iloc[idx]['voter'])
                if member_id in self.members:
                    member = Person.objects.get(id_parladata=member_id)
                    most_data.append({'member': member,
                                      'score': data.iloc[idx][mp]})
            most_data = list(reversed(most_data))

            result = saveOrAbortNew(model=EqualVoters,
                                    created_for=self.date_of,
                                    person=person,
                                    person1=most_data[0]['member'],
                                    votes1=most_data[0]['score'],
                                    person2=most_data[1]['member'],
                                    votes2=most_data[1]['score'],
                                    person3=most_data[2]['member'],
                                    votes3=most_data[2]['score'],
                                    person4=most_data[3]['member'],
                                    votes4=most_data[3]['score'],
                                    person5=most_data[4]['member'],
                                    votes5=most_data[4]['score'])

            # less equal
            less_data = []
            data = mps_data
            #for idx in range(5):
            idx = 0
            while len(less_data) < 5:
                member_id = int(data.iloc[idx]['voter'])
                if member_id in self.members:
                    member = Person.objects.get(id_parladata=member_id)
                    less_data.append({'member': member,
                                      'score': data.iloc[idx][mp]})
                idx += 1

            result = saveOrAbortNew(model=LessEqualVoters,
                                    created_for=self.date_of,
                                    person=person,
                                    person1=less_data[0]['member'],
                                    votes1=less_data[0]['score'],
                                    person2=less_data[1]['member'],
                                    votes2=less_data[1]['score'],
                                    person3=less_data[2]['member'],
                                    votes3=less_data[2]['score'],
                                    person4=less_data[3]['member'],
                                    votes4=less_data[3]['score'],
                                    person5=less_data[4]['member'],
                                    votes5=less_data[4]['score'])

    def setEqualVotesPG(self):
        """
        set cards how equal are voters to Partys
        """
        results = self.equalVotersPGData
        for pg in results.keys():
            org = Organization.objects.get(id_parladata=int(pg))
            r = results[pg]
            r = r.reset_index().sort_values(pg, ascending=False)
            print(self.memsOfPGs)
            if int(pg) not in self.memsOfPGs.keys():
                "if this PG hasn't members on this time"
                continue
            # TODO notify someone if this fails
            thisPG = r[r.voter.isin(self.memsOfPGs[int(pg)])]
            otherMembers = [m
                            for pg_key
                            in self.memsOfPGs.keys()
                            if pg_key != str(pg)
                            for m
                            in self.memsOfPGs[pg_key]
                            ]
            print 'pg', pg, len(self.memsOfPGs[pg]), len(otherMembers)
            otherMems = r[r.voter.isin(otherMembers)]

            # most equal
            most_data = []
            data = otherMems
            # for idx in range(5):
            for idx in range(len(data)-1):
                member_id = int(data.iloc[idx]['voter'])
                if member_id in self.members:
                    member = Person.objects.get(id_parladata=member_id)
                    most_data.append({'member': member,
                                      'score': data.iloc[idx][pg]})
            most_data = list(reversed(most_data))

            result = saveOrAbortNew(model=MostMatchingThem,
                                    created_for=self.date_of,
                                    organization=org,
                                    person1=most_data[0]['member'],
                                    votes1=most_data[0]['score'],
                                    person2=most_data[1]['member'],
                                    votes2=most_data[1]['score'],
                                    person3=most_data[2]['member'],
                                    votes3=most_data[2]['score'],
                                    person4=most_data[3]['member'],
                                    votes4=most_data[3]['score'],
                                    person5=most_data[4]['member'],
                                    votes5=most_data[4]['score'])
            # less equal
            less_data = []
            data = otherMems
            #for idx in range(5):
            idx = 0
            while len(less_data) < 5:
                member_id = int(data.iloc[idx]['voter'])
                if member_id in self.members:
                    member = Person.objects.get(id_parladata=member_id)
                    less_data.append({'member': member,
                                      'score': data.iloc[idx][pg]})
                idx += 1

            result = saveOrAbortNew(model=LessMatchingThem,
                                    created_for=self.date_of,
                                    organization=org,
                                    person1=less_data[0]['member'],
                                    votes1=less_data[0]['score'],
                                    person2=less_data[1]['member'],
                                    votes2=less_data[1]['score'],
                                    person3=less_data[2]['member'],
                                    votes3=less_data[2]['score'],
                                    person4=less_data[3]['member'],
                                    votes4=less_data[3]['score'],
                                    person5=less_data[4]['member'],
                                    votes5=less_data[4]['score'])
            # deviation
            print thisPG
            dev_data = []
            for idx in range(thisPG.count()['voter']):
                dev_data.append({'id': thisPG.iloc[idx]['voter'],
                                 'ratio': thisPG.iloc[idx][pg]})
            result = saveOrAbortNew(model=DeviationInOrganization,
                                    created_for=self.date_of,
                                    organization=org,
                                    data=dev_data
                                    )

    def setPresenceMPs(self):
        """
        set presence for all Members
        """
        votes = self.presenceMP_V
        sessions = self.presenceMP_S

        actualVotes = votes[votes.voter.isin(self.members)]
        avgVote = actualVotes[['attendance']].mean().attendance
        maxVote = actualVotes.max()
        max_vote_value = actualVotes['attendance'].max()
        max_vote_voters = actualVotes[actualVotes.attendance == max_vote_value]['voter'].tolist()

        actualSession = sessions[sessions.voter.isin(self.members)]
        avgSession = actualSession[['attendance']].mean().attendance
        max_session_value = actualSession['attendance'].max()
        max_ses_voters = actualSession[actualSession.attendance == max_session_value]['voter'].tolist()

        for mp in self.members:
            try:
                person = Person.objects.get(id_parladata=int(mp))
                thisVotes = votes[votes.voter == mp].reset_index().at[0, 'attendance']
                tempS = sessions[sessions.voter == mp].reset_index()
                thisSession = tempS.at[0, 'attendance']
                print mp

                result = saveOrAbortNew(model=Presence,
                                        created_for=self.date_of,
                                        person=person,
                                        person_value_sessions=thisSession,
                                        maxMP_sessions=max_ses_voters,
                                        average_sessions=avgSession,
                                        maximum_sessions=max_session_value,
                                        person_value_votes=thisVotes,
                                        maxMP_votes=max_vote_voters,
                                        average_votes=avgVote,
                                        maximum_votes=max_vote_value)
            except:
                print mp, 'fail set presence'

    def setPresenceOfPGs(self):
        """
        set presence for all Partys
        """
        table = self.presencePGs

        averageSessions = table['sessions'].mean()
        averageVotes = table['votes'].mean()

        maxVotes = table['votes'].max()
        maxVotesOrgIdx = table['votes'].idxmax()

        maxSessions = table['sessions'].max()
        maxSessionOrgIdx = table['sessions'].idxmax()

        for pg in self.pgs:
            try:
                thisSessions = table[table.pg == pg].sessions[pg]
                thisVotes = table[table.pg == pg].votes[pg]
            except:
                continue
            thisOrg = Organization.objects.get(id_parladata=pg)
            result = saveOrAbortNew(model=PercentOFAttendedSession,
                                    created_for=self.date_of,
                                    organization=thisOrg,
                                    organization_value_sessions=thisSessions,
                                    maxPG_sessions=[maxSessionOrgIdx],
                                    average_sessions=averageSessions,
                                    maximum_sessions=maxSessions,
                                    organization_value_votes=thisVotes,
                                    maxPG_votes=[maxVotesOrgIdx],
                                    average_votes=averageVotes,
                                    maximum_votes=maxVotes)

    def setAll(self):
        """
        set all vote cards
        """
        self.setPresenceMPs()
        self.setPresenceOfPGs()
        self.setEqualVoters()
        self.setEqualVotesPG()


def setAllVotesCards():
    for org_id in getParentOrganizationsWithVoters():
        votesObj = VotesAnalysis(organization_id=org_id)
        votesObj.setAll()
        return 'All is well'
