from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, Presence
from parlalize.utils_ import saveOrAbortNew
from utils.parladata_api import getVotersIDs, getParentOrganizationsWithVoters, getNumberOfAllMPAttendedSessions
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT

def setPercentOFAttendedSession(commander, members, date_of=datetime.now().date()):

    data = getNumberOfAllMPAttendedSessions(date_of, members)
    for person_id in members:

        if not data["votes"].values():
            commander.stdout.write('Member with id: %s has not votes' % str(person_id))
            return

        if person_id in data["sessions"].keys():
            thisMP = data["sessions"][person_id]
        else:
            # ta member se ni obstajal
            commander.stdout.write('Member with id %s didn\'t exist' % str(person_id))
            return

        org_sessions_values = [value for key, value in data["sessions"].items() if int(key) in members]
        maximum = max(org_sessions_values)
        maximumMP = [pId for pId in data["sessions"]
                    if data["sessions"][pId] == maximum and int(pId) in members]
        average = sum(org_sessions_values) / len(org_sessions_values)

        if person_id in data["votes"].keys():
            thisMPVotes = data["votes"][person_id]
        else:
            thisMPVotes = 0

        org_votes_values = [value for key, value in data["votes"].items() if int(key) in members]
        maximumVotes = max(org_votes_values)
        maximumMPVotes = [pId for pId in data["votes"]
                        if data["votes"][pId] == maximumVotes and int(pId) in members]

        averageVotes = sum(org_votes_values) / len(org_votes_values)

        person = Person.objects.get(id_parladata=int(person_id))

        result = saveOrAbortNew(model=Presence,
                                created_for=date_of,
                                person=person,
                                person_value_sessions=thisMP,
                                maxMP_sessions=maximumMP,
                                average_sessions=average,
                                maximum_sessions=maximum,
                                person_value_votes=thisMPVotes,
                                maxMP_votes=maximumMPVotes,
                                average_votes=averageVotes,
                                maximum_votes=maximumVotes)

        commander.stdout.write('Set Presence for member with id %s' % str(person_id))


class Command(BaseCommand):
    help = 'Updates MPs\' persence data'

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

        for org_id in getParentOrganizationsWithVoters():
            members = getVotersIDs(organization_id=org_id)
            setPercentOFAttendedSession(self, members, date_of)
        return 0
