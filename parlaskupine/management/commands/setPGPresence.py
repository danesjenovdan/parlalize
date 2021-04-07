from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaskupine.models import Organization, PercentOFAttendedSession
from parlalize.utils_ import saveOrAbortNew
from utils.parladata_api import (getParentOrganizationsWithVoters,
    getVotersIDs, getVotersPairsWithOrg, getOrganizationsWithVoters, getNumberOfAllMPAttendedSessions)
from datetime import datetime
from django.conf import settings

def setPercentOFAttendedSessionPG(pg_id, date_of, parenet_org):

    date_ = date_of.strftime(settings.API_DATE_FORMAT)

    allSum = {}
    data = {}

    voters = getVotersPairsWithOrg(date_=date_of, organization_id=parenet_org)
    membersOfPG = {}

    for i, value in sorted(voters.iteritems()):
        membersOfPG.setdefault(value, []).append(i)

    data = getNumberOfAllMPAttendedSessions(date_of, getVotersIDs(date_=date_of, organization_id=parenet_org))

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
                         if sessions[pgId] == maximumSessions][:5]
    averageSessions = sum(data['sessions'].values()) / len(data['sessions'])

    thisMPVotes = votes[pg_id]
    maximumVotes = max(votes.values())
    maximumPGVotes = [pgId
                      for pgId
                      in votes
                      if votes[pgId] == maximumVotes][:5]
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


class Command(BaseCommand):
    help = 'Updates MPs\' persence data'

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        for parent_id in getParentOrganizationsWithVoters():
            mps = getVotersIDs(date_=date_of, organization_id=parent_id)
            for org_id in getOrganizationsWithVoters(organization_id=parent_id, date_=date_of):
                setPercentOFAttendedSessionPG(org_id, date_of=date_of, parenet_org=parent_id)
