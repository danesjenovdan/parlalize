from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaseje.models import Session, Legislation, Vote, AgendaItem, AmendmentOfOrg
from parlaskupine.models import Organization
from parlaseje.utils_ import getMotionClassification
from parlalize.settings import API_URL, DZ, SETTER_KEY, YES, AGAINST, ABSTAIN, NOT_PRESENT
from parlalize.utils_ import tryHard, saveOrAbortNew
from utils.votes_outliers import setMotionAnalize
from utils.delete_renders import deleteRendersOfSessionVotes
from utils.legislations import finish_legislation_by_final_vote
from django.test.client import RequestFactory

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

def setMotionOfSession(commander, session_id):
    """Stores all motions with detiled data of specific sesison.
    """
    commander.stdout.write('Beginning setMotionOfSession for session %s' % str(session_id))
    commander.stdout.write('Trying hard for %s/motionOfSession/%s/' % (API_URL, str(session_id)))
    motion = tryHard(API_URL + '/motionOfSession/' + str(session_id) + '/').json()
    session = Session.objects.get(id_parladata=session_id)
    yes = 0
    no = 0
    kvorum = 0
    not_present = 0
    laws = []
    for mot in motion:
        commander.stdout.write('Handling motion %s' % str(mot['id']))
        url = API_URL + '/getBallotsOfMotion/' + str(mot['vote_id']) + '/'
        commander.stdout.write('Trying hard for %s' % url)
        votes = tryHard(url).json()
        for vote in votes:
            if vote['option'] in YES:
                yes += 1
            if vote['option'] in AGAINST:
                no += 1
            if vote['option'] in ABSTAIN:
                kvorum += 1
            if vote['option']  in NOT_PRESENT:
                not_present += 1

        if mot['counter']:
            # this is for votes without ballots
            opts_set = set(mot['counter'].keys())
            if opts_set.intersection(YES):
                yes = mot['counter']['for']
            if opts_set.intersection(AGAINST):
                no = mot['counter']['against']
            if opts_set.intersection(ABSTAIN):
                kvorum = mot['counter']['abstain']
            # hardcoded croations number of member
            not_present = 151 - sum([int(v) for v in mot['counter'].values()])

        result = mot['result']
        if mot['amendment_of']:
            a_orgs = list(Organization.objects.filter(id_parladata__in=mot['amendment_of']))
        else:
            a_orgs = []

        if mot['amendment_of_people']:
            a_people = Person.objects.filter(id_parladata__in=mot['amendment_of_people'])
        else:
            a_people = []

        # TODO: replace try with: "if mot['epa']"
        try:
            law = Legislation.objects.get(epa=mot['epa'])
            laws.append(law)
        except:
            law = None

        classification = getMotionClassification(mot['text'])
        vote = Vote.objects.filter(id_parladata=mot['vote_id'])

        agendaItems = list(AgendaItem.objects.filter(id_parladata__in=mot['agenda_item_ids']))

        if vote:
            commander.stdout.write('Updating vote %s' % str(mot['vote_id']))
            prev_result = vote[0].result
            vote.update(created_for=session.start_time,
                        start_time=mot['start_time'],
                        session=session,
                        motion=mot['text'],
                        tags=mot['tags'],
                        votes_for=yes,
                        against=no,
                        abstain=kvorum,
                        not_present=not_present,
                        result=result,
                        id_parladata=mot['vote_id'],
                        document_url=mot['doc_url'],
                        epa=mot['epa'],
                        law=law,
                        classification=classification,
                        )
            vote[0].amendment_of.clear()
            for org in  a_orgs:
                AmendmentOfOrg(vote=vote[0], organization=org).save()
            vote[0].amendment_of_person.add(*a_people)

            vote[0].agenda_item.add(*agendaItems)

            if prev_result != vote[0].result:
                commander.stdout.write('Running finish_legislation_by_final_vote(vote[0])')
                finish_legislation_by_final_vote(vote[0])
        else:
            commander.stdout.write('Saving new vote %s' % str(mot['vote_id']))
            result = saveOrAbortNew(model=Vote,
                                    created_for=session.start_time,
                                    start_time=mot['start_time'],
                                    session=session,
                                    motion=mot['text'],
                                    tags=mot['tags'],
                                    votes_for=yes,
                                    against=no,
                                    abstain=kvorum,
                                    not_present=not_present,
                                    result=result,
                                    id_parladata=mot['vote_id'],
                                    document_url=mot['doc_url'],
                                    epa=mot['epa'],
                                    law=law,
                                    classification=classification,
                                    )
            if a_orgs:
                vote = Vote.objects.filter(id_parladata=mot['vote_id'])
                vote[0].amendment_of.clear()
                for org in  a_orgs:
                    AmendmentOfOrg(vote=vote[0], organization=org).save()
                vote[0].amendment_of_person.add(*a_people)
                vote[0].agenda_item.add(*agendaItems)
                commander.stdout.write('Running finish_legislation_by_final_vote(vote[0])')
                finish_legislation_by_final_vote(vote[0])

        yes = 0
        no = 0
        kvorum = 0
        not_present = 0

    # set motion analize
    commander.stdout.write('Running setMotionAnalize for %s' % str(session_id))
    setMotionAnalize(None, session_id)

    # TODO figure out what to do with this
    # if laws:
    #     recacheLegislationsOnSession(session_id)

    commander.stdout.write('Running deleteRendersOfSessionVotes for %s' % str(session_id))
    deleteRendersOfSessionVotes(session_id)

    return 0

class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def handle(self, *args, **options):
      ses = Session.objects.all()
      for s in ses:
          self.stdout.write('Updating session %s' % str(s.id_parladata))
          status = setMotionOfSession(self, str(s.id_parladata))
          self.stdout.write('setMotionOfSession returned %s' % str(status))
      
      return 0
