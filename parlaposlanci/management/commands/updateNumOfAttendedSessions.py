from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, Presence
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT

def setPercentOFAttendedSession(commander, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    data = tryHard(API_URL+'/getNumberOfAllMPAttendedSessions/'+date_).json()

    if not data["votes"].values():
        commander.stdout.write('Member with id: %s has not votes' % str(person_id))
        return

    if person_id in data["sessions"].keys():
        thisMP = data["sessions"][person_id]
    else:
        # ta member se ni obstajal
        commander.stdout.write('Member with id %s didn\'t exist' % str(person_id))
        return

    maximum = max(data["sessions"].values())
    maximumMP = [pId for pId in data["sessions"]
                 if data["sessions"][pId] == maximum]
    average = sum(data["sessions"].values()) / len(data["sessions"])

    if person_id in data["votes"].keys():
        thisMPVotes = data["votes"][person_id]
    else:
        thisMPVotes = 0

    maximumVotes = max(data["votes"].values())
    maximumMPVotes = [pId for pId in data["votes"]
                      if data["votes"][pId] == maximumVotes]

    averageVotes = sum(data["votes"].values()) / len(data["votes"])

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
        memberships = tryHard(API_URL + '/getMPs/' + date_).json()

        for membership in memberships:
            setPercentOFAttendedSession(self, str(membership['id']))
        return 0
