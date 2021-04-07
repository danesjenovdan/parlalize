from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.test.client import RequestFactory
from django.db.models import Q

from parlaposlanci.models import Person
from parlaskupine.models import Organization
from parlaseje.models import Session, Legislation, Vote, AgendaItem, AmendmentOfOrg
from parlaseje.utils_ import getMotionClassification
from parlalize.settings import SETTER_KEY, YES, AGAINST, ABSTAIN, NOT_PRESENT
from parlalize.utils_ import tryHard, saveOrAbortNew

from utils.votes_outliers import setMotionAnalize
from utils.delete_renders import deleteRendersOfSession
from utils.legislations import finish_legislation_by_final_vote
from utils import parladata_api

import operator
import re
import json


factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

def hasNumbersOrPdfOrEndWord(inputString):
    end_words = ['PZE', 'PZ', 'P.Z.E.']
    has_number = any(char.isdigit() for char in inputString)
    has_pdf = 'pdf' in inputString
    is_end_word = inputString in end_words
    return has_number or has_pdf or is_end_word

def getOwnersOfAmendment(vote):
    orgs_ids = []
    people_ids = []
    if settings.COUNTRY == 'SI':
        if 'Amandma' in vote.motion:
            acronyms = re.findall('\; \s*(\w+)|\[\s*(\w+)', vote.motion)
            acronyms = [pg[0] + ',' if pg[0] else pg[1] + ',' for pg in acronyms]
            if acronyms:
                query = reduce(operator.or_, (Q(name_parser__icontains=item) for item in acronyms))
                orgs = Organization.objects.filter(query)
                s_time = vote.start_time
                #orgs = orgs.filter(Q(founding_date__lte=s_time) |
                #                   Q(founding_date=None),
                #                   Q(dissolution_date__gte=s_time) |
                #                   Q(dissolution_date=None))
                org_ids = list(orgs.values_list('id_parladata', flat=True))
            else:
                org_ids = []
        else:
            org_ids = []
        return {'orgs': org_ids, 'people': []}
    elif settings.COUNTRY == 'HR':
        amendment_words = ['AMANDMANI', 'AMANDMAN']
        links = vote.document_url if vote.document_url else []
        org_ids = parladata_api.getOrganizationsWithVoters()
        orgs = Organization.objects.filter(id_parladata__in = org_ids)
        acronyms = {}
        for org in orgs:
            acronyms[' '.join(org.acronym.split(', '))]= org.id
        vlada_id = Organization.objects.get(name='Vlada').id
        acronyms['Vlada VladaRH']= vlada_id
        for link in links:
            tokens = link.name.replace(" ", '_').replace("-", '_').split('_')
            print(link.name)
            if 'AMANDMAN' in link.name:
                for acronym, i in acronyms.items():
                    # find orgs
                    for splited_acr in acronym.split(' '):
                        if splited_acr in link.name:
                            orgs_ids.append(i)
                            break
                num_ids = [hasNumbersOrPdfOrEndWord(token) for token in tokens]
                if True in num_ids:
                    tokens = tokens[:num_ids.index(True)]
                has_amendment = [token in amendment_words for token in tokens]
                if True in has_amendment:
                    tokens = tokens[has_amendment.index(True)+1:]
                # find proposers
                #if tokens[0].lower() == 'vlada' or tokens[0].lower() == 'vladarh':
                    # vlada
                elif tokens[0].lower() == 'klub':
                    tokens = tokens[1:]

                n_tokens = len(tokens)
                for i in range(n_tokens):
                    d_tokens = [[tokens[i]]]
                    if i + 1 < n_tokens:
                        d_tokens.append([tokens[i], tokens[i+1]])
                    for d_token in d_tokens:
                        n_tokens = len(tokens)
                        for i in range(n_tokens):
                            d_tokens = [[tokens[i]]]
                            if i + 1 < n_tokens:
                                d_tokens.append([tokens[i], tokens[i+1]])
                            for d_token in d_tokens:
                                person = Person.objects.filter(name_parser__icontains=' '.join(d_token))
                                if person.count() == 1:
                                    people_ids.append(person[0].id)
                                    break
                                if person.count() > 0:
                                    names = person.values('id', 'name_parser')
                                    for name in names:
                                        if re.search("\\b" + ' '.join(d_token) + "\\b", name['name_parser']):
                                            people_ids.append(name['id'])
                                            break
        print(acronyms)
    return {'orgs': orgs_ids, 'people': list(set(people_ids))}

def setMotionOfSession(commander, session_id):
    """Stores all motions with detiled data of specific sesison.
    """
    if commander:
        commander.stdout.write('Beginning setMotionOfSession for session %s' % str(session_id))
        commander.stdout.write('Getting for motion for session %s' % (str(session_id)))
    votes = parladata_api.getVotesForSession(session_id)
    session = Session.objects.get(id_parladata=session_id)

    laws = []
    for vote in votes:
        if commander:
            commander.stdout.write('Handling vote %s' % str(vote['id']))

        if not vote['name']:
            commander.stdout.write('Skipping vote because it has no name: %s' % str(vote['id']))

        motion = parladata_api.getMotion(vote['motion'])

        if vote['results']:
            votes_for = vote['results']['for']
            votes_against = vote['results']['against']
            votes_abstain = vote['results']['abstain']
            votes_absent = vote['results']['absent']

        if vote['counter']:
            # this is for votes without ballots
            counter = json.loads(vote['counter'])
            opts_set = set(counter.keys())
            if opts_set.intersection(YES):
                votes_for = counter['for']
            if opts_set.intersection(AGAINST):
                votes_against = counter['against']
            if opts_set.intersection(ABSTAIN):
                votes_abstain = counter['abstain']
            # hardcoded croations number of member
            votes_absent = 151 - sum([int(v) for v in counter.values()])

        result = motion['result']
        documents = [{'url': link['url'], 'name': link['url']} for link in motion['links']]

        # TODO: replace try with: "if vote['epa']"
        try:
            law = Legislation.objects.get(epa=motion['epa'])
            laws.append(law)
        except:
            law = None

        classification = getMotionClassification(vote['name'])
        vote_obj = Vote.objects.filter(id_parladata=vote['id'])

        agendaItems = list(AgendaItem.objects.filter(id_parladata__in=motion['agenda_item']))

        if vote_obj:
            if commander:
                commander.stdout.write('Updating vote %s' % str(vote['id']))
                commander.stdout.write('Updating data %s' % str(vote))
            prev_result = vote_obj[0].result
            vote_obj.update(created_for=session.start_time,
                        start_time=vote['start_time'],
                        session=session,
                        motion=vote['name'],
                        tags=vote['tags'],
                        votes_for=votes_for,
                        against=votes_against,
                        abstain=votes_abstain,
                        not_present=votes_absent,
                        result=result,
                        id_parladata=vote['id'],
                        document_url=documents,
                        epa=motion['epa'],
                        law=law,
                        classification=classification,
                        )
            vote_obj = vote_obj[0]
            vote_obj.agenda_item.add(*agendaItems)

            if prev_result != vote_obj.result:
                if commander:
                    commander.stdout.write('Running finish_legislation_by_final_vote(vote[0])')
                finish_legislation_by_final_vote(vote_obj)
        else:
            if commander:
                commander.stdout.write('Saving new vote %s' % str(vote['id']))
            result = saveOrAbortNew(model=Vote,
                                    created_for=session.start_time,
                                    start_time=vote['start_time'],
                                    session=session,
                                    motion=vote['name'],
                                    tags=vote['tags'],
                                    votes_for=votes_for,
                                    against=votes_against,
                                    abstain=votes_abstain,
                                    not_present=votes_absent,
                                    result=result,
                                    id_parladata=vote['id'],
                                    document_url=documents,
                                    epa=motion['epa'],
                                    law=law,
                                    classification=classification,
                                    )
            vote_obj = Vote.objects.get(id_parladata=vote['id'])
            commander.stdout.write('Running finish_legislation_by_final_vote(vote[0])')
            finish_legislation_by_final_vote(vote_obj)

        owners = getOwnersOfAmendment(vote_obj)
        if owners['orgs']:
            a_orgs = list(Organization.objects.filter(id_parladata__in=owners['orgs']))
        else:
            a_orgs = []

        if owners['people']:
            a_people = Person.objects.filter(id_parladata__in=owners['people'])
        else:
            a_people = []

        if a_orgs:
            vote_obj.amendment_of.clear()
            for org in  a_orgs:
                AmendmentOfOrg(vote=vote_obj, organization=org).save()
            vote_obj.amendment_of_person.add(*a_people)

    # set motion analize
    if commander:
        commander.stdout.write('Running setMotionAnalize for %s' % str(session_id))
    setMotionAnalize(session_id)

    # TODO figure out what to do with this
    # if laws:
    #     recacheLegislationsOnSession(session_id)

    if commander:
        commander.stdout.write('Running deleteRendersOfSessionVotes for %s' % str(session_id))
    deleteRendersOfSession([session_id])

    return 0

class Command(BaseCommand):
    help = 'Update motion of session - what?'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session_ids',
            nargs='+',
            help='IDs of session to run this for',
        )

    def handle(self, *args, **options):
        session_ids = []
        if options['session_ids']:
            session_ids = options['session_ids']
        else:
            session_ids = Session.objects.all().values_list('id_parladata', flat=True)

        for s in session_ids:
            self.stdout.write('Updating session %s' % str(s))
            status = setMotionOfSession(self, str(s))
            self.stdout.write('setMotionOfSession returned %s' % str(status))

        return 0
