from django.core.management.base import BaseCommand, CommandError
from django.test.client import RequestFactory

from parlalize.settings import API_URL, slack_token, API_DATE_FORMAT, DZ, SETTER_KEY, LEGISLATION_STATUS
from parlalize.utils_ import tryHard

from parlaseje.models import Ballot, Vote, Speech, Question, Legislation, Session
from parlaseje.views import getSessionsList
from parlaseje.utils_ import speech_the_order
from parlaposlanci.models import Person, MinisterStatic
from parlaskupine.models import Organization
from utils.imports import importDraftLegislationsFromFeed
#from utils.runner import runSettersSessions
from parlaposlanci.management.commands.updateMotionOfSession import *
from utils.delete_renders import delete_renders, deleteRendersOfSession, deleteRendersOfIDs, refetch

from utils.parladata_api import getVotersIDs

from datetime import datetime, timedelta
from slackclient import SlackClient
from time import time
from itertools import groupby


class Command(BaseCommand):
    help = 'Delete all card renders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date for which to run the card',
        )

    def getModelStartTime(self, model):
        try:
            lastObjectTime = model.objects.latest('updated_at').updated_at
        except:
            lastObjectTime = datetime(day=1, month=1, year=2000)
        return lastObjectTime

    def handle(self, *args, **options):
        factory = RequestFactory()
        request_with_key = factory.get('?key=' + SETTER_KEY)

        fast = False
        date_ = None
        sc = SlackClient(slack_token)
        start_time = time()
        yesterday = (datetime.now()-timedelta(days=1)).date()
        yesterday = datetime.combine(yesterday, datetime.min.time())
        new_redna_seja = []
        lockFile = open('parser.lock', 'w+')
        lockFile.write('LOCKED')
        lockFile.close()
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='Start fast update at: ' + str(datetime.now()))
        dates = []

        lastBallotTime = self.getModelStartTime(Ballot)
        lastVoteTime = self.getModelStartTime(Vote)
        lastSpeechTime = self.getModelStartTime(Speech)
        lastQustionTime = self.getModelStartTime(Question)
        lastLegislationTime = self.getModelStartTime(Legislation)
        if date_:
            dates = [date_ + '_00:00' for i in range(5)]
        else:
            # get dates of last update
            dates.append(self.getModelStartTime(Person))
            dates.append(self.getModelStartTime(Session))
            dates.append(datetime.now()-timedelta(days=1))#lastSpeechTime)
            dates.append(lastBallotTime)
            dates.append(lastQustionTime)

            #lastLegislationTime=datetime.now()-timedelta(days=10)
            dates.append(lastLegislationTime)

        # prepare url
        url = API_URL + '/getAllChangesAfter/'
        for sDate in dates:
            url += sDate.strftime(API_DATE_FORMAT + '_%H:%M') + '/'

        self.stdout.write(url)

        data = tryHard(url[:-1]).json()

        self.stdout.write('Speeches: ' + str(len(data['speeches'])))
        self.stdout.write('Sessions: ' + str(len(data['sessions'])))
        self.stdout.write('Persons: ' + str(len(data['persons'])))
        self.stdout.write('Questions: ' + str(len(data['questions'])))
        self.stdout.write('Legislation: ' + str(len(data['laws'])))

        text = ('Received data: \n'
                'Speeches: ' + str(len(data['speeches'])) + '\n'
                'Sessions: ' + str(len(data['sessions'])) + '\n'
                'Persons: ' + str(len(data['persons'])) + '\n'
                'Questions: ' + str(len(data['questions'])) + '\n'
                'Legislation: ' + str(len(data['laws'])) + '\n'
                )
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text=text)

        sdate = datetime.now().strftime(API_DATE_FORMAT)

        # Persons
        mps_ids = getVotersIDs()
        for mp in data['persons']:
            if Person.objects.filter(id_parladata=mp['id']):
                person = Person.objects.get(id_parladata=mp['id'])
                person.name = mp['name']
                person.pg = mp['membership']
                person.id_parladata = int(mp['id'])
                person.image = mp['image']
                person.actived = True if int(mp['id']) in mps_ids else False
                person.gov_id = mp['gov_id']
                person.save()
            else:
                actived = True if int(mp['id']) in mps_ids else False
                person = Person(name=mp['name'],
                                pg=mp['membership'],
                                id_parladata=int(mp['id']),
                                image=mp['image'],
                                actived=actived,
                                gov_id=mp['gov_id'])
                person.save()

        session_ids = list(Session.objects.all().values_list('id_parladata',
                                                            flat=True))

        # sessions
        for sessions in data['sessions']:
            orgs = Organization.objects.filter(id_parladata__in=sessions['organizations_id'])
            if not orgs:
                orgs = Organization.objects.filter(id_parladata=sessions['organization_id'])
            if sessions['id'] not in session_ids:
                result = Session(name=sessions['name'],
                                gov_id=sessions['gov_id'],
                                start_time=sessions['start_time'],
                                end_time=sessions['end_time'],
                                classification=sessions['classification'],
                                id_parladata=sessions['id'],
                                organization=orgs[0],
                                in_review=sessions['is_in_review']
                                )
                result.save()
                orgs = list(orgs)
                result.organizations.add(*orgs)
                if sessions['id'] == DZ:
                    if 'redna seja' in sessions['name'].lower():
                        # call method for create new list of members
                        #new_redna_seja.append(sessions)
                        pass
            else:
                if not Session.objects.filter(name=sessions['name'],
                                            gov_id=sessions['gov_id'],
                                            start_time=sessions['start_time'],
                                            end_time=sessions['end_time'],
                                            classification=sessions['classification'],
                                            id_parladata=sessions['id'],
                                            organization=orgs[0],
                                            in_review=sessions['is_in_review']):
                    # save changes
                    session = Session.objects.get(id_parladata=sessions['id'])
                    session.name = sessions['name']
                    session.gov_id = sessions['gov_id']
                    session.start_time = sessions['start_time']
                    session.end_time = sessions['end_time']
                    session.classification = sessions['classification']
                    session.in_review = sessions['is_in_review']
                    session.save()
                    orgs = list(orgs)
                    session.organizations.add(*orgs)

        # update Legislation
        for epa, laws in groupby(data['laws'], lambda item: item['epa']):
            last_obj = None
            sessions = []
            is_ended = False
            for law in laws:
                sessions.append(law['session'])
                law['date'] = datetime.strptime(law['date'], '%Y-%m-%dT%X')
                if not is_ended:
                    if law['procedure_ended']:
                        is_ended = True
                if last_obj:
                    if law['date'] > last_obj['date']:
                        last_obj = law
                else:
                    last_obj = law
            result = Legislation.objects.filter(epa=epa)

            # dont update Legislatin procedure_ended back to False
            if result:
                result = result[0]
                if result.procedure_ended:
                    is_ended = True

                self.stdout.write('update')
                result.text = last_obj['text']
                result.mdt = last_obj['mdt']
                result.proposer_text = last_obj['proposer_text']
                result.procedure_phase = last_obj['procedure_phase']
                result.procedure = last_obj['procedure']
                result.type_of_law = last_obj['type_of_law']
                result.id_parladata = last_obj['id']
                result.date = last_obj['date']
                result.procedure_ended = is_ended
                result.classification = last_obj['classification']
                result.save()
            else:
                self.stdout.write('adding')
                result = Legislation(text=last_obj['text'],
                                    epa=last_obj['epa'],
                                    mdt=last_obj['mdt'],
                                    proposer_text=last_obj['proposer_text'],
                                    procedure_phase=last_obj['procedure_phase'],
                                    procedure=last_obj['procedure'],
                                    type_of_law=last_obj['type_of_law'],
                                    id_parladata=last_obj['id'],
                                    date=last_obj['date'],
                                    procedure_ended=is_ended,
                                    classification=last_obj['classification'],
                                    result=LEGISLATION_STATUS[0][0]
                                    )
                result.save()
            sessions = list(set(sessions))
            sessions = list(Session.objects.filter(id_parladata__in=sessions))
            result.sessions.add(*sessions)
            self.stdout.write(epa)

        # update speeches
        existingIDs = list(Speech.objects.all().values_list('id_parladata',
                                                            flat=True))
        sc.api_call('chat.postMessage',
                    channel='#parlalize_notif',
                    text='Start update speeches at: ' + str(datetime.now()))
        for dic in data['speeches']:
            if int(dic['id']) not in existingIDs:
                self.stdout.write('adding speech')
                person = Person.objects.get(id_parladata=int(dic['speaker']))
                speech = Speech(organization=Organization.objects.get(
                                    id_parladata=int(dic['party'])),
                                content=dic['content'],
                                agenda_item_order=dic['agenda_item_order'],
                                order=dic['order'],
                                session=Session.objects.get(
                                    id_parladata=int(dic['session'])),
                                start_time=dic['start_time'],
                                end_time=dic['end_time'],
                                valid_from=dic['valid_from'],
                                valid_to=dic['valid_to'],
                                id_parladata=dic['id'])
                speech.save()
                speech.person.add(person)
            else:
                self.stdout.write('update speech')
                person = Person.objects.get(id_parladata=int(dic['speaker']))
                speech = Speech.objects.filter(id_parladata=dic["id"])
                speech.update(content=dic['content'],
                            valid_from=dic['valid_from'],
                            valid_to=dic['valid_to'])

        # update Votes
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='Start update votes at: ' + str(datetime.now()))
        for session_id in data['sessions_of_updated_votes']:
            self.stdout.write('set motion of session ' + str(session_id))
            c=Command()
            setMotionOfSession(c, str(session_id))

        # update ballots
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='Start update ballots at: ' + str(datetime.now()))
        existingISs = Ballot.objects.all().values_list('id_parladata', flat=True)
        for dic in data['ballots']:
            if int(dic['id']) not in existingISs:
                self.stdout.write('adding ballot ' + str(dic['vote']))
                vote = Vote.objects.get(id_parladata=dic['vote'])
                person = Person.objects.get(id_parladata=int(dic['voter']))
                ballots = Ballot(option=dic['option'],
                                vote=vote,
                                start_time=vote.start_time,
                                end_time=None,
                                id_parladata=dic['id'],
                                voter_party = Organization.objects.get(id_parladata=dic['voterparty']))
                ballots.save()
                ballots.person.add(person)

        # update questions
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='Start update Questions at: ' + str(datetime.now()))
        existingISs = list(Question.objects.all().values_list('id_parladata',
                                                            flat=True))
        for dic in data['questions']:
            if int(dic['id']) not in existingISs:
                self.stdout.write('adding question')
                if dic['session_id']:
                    session = Session.objects.get(id_parladata=int(dic['session_id']))
                else:
                    session = None
                link = dic['link'] if dic['link'] else None
                person = []
                for i in dic['author_id']:
                    person.append(Person.objects.get(id_parladata=int(i)))
                if dic['recipient_id']:
                    rec_p = list(Person.objects.filter(id_parladata__in=dic['recipient_id']))
                else:
                    rec_p = []
                if dic['recipient_org_id']:
                    rec_org = list(Organization.objects.filter(id_parladata__in=dic['recipient_org_id']))
                else:
                    rec_org = []
                author_org = []
                for i in dic['author_org_id']:
                    author_org.append(Organization.objects.get(id_parladata=i))
                rec_posts = []
                for post in dic['recipient_posts']:
                    static = MinisterStatic.objects.filter(person__id_parladata=post['membership__person_id'],
                                                        ministry__id_parladata=post['organization_id']).order_by('-created_for')
                    if static:
                        rec_posts.append(static[0])
                question = Question(session=session,
                                    start_time=dic['date'],
                                    id_parladata=dic['id'],
                                    recipient_text=dic['recipient_text'],
                                    title=dic['title'],
                                    content_link=link,
                                    )
                question.save()
                question.person.add(*person)
                question.author_orgs.add(*author_org)
                question.recipient_persons.add(*rec_p)
                question.recipient_organizations.add(*rec_org)
                question.recipient_persons_static.add(*rec_posts)

        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='Start update distircts and tags at: ' + str(datetime.now()))

        t_delta = time() - start_time

        text = ('End fast update (' + str(t_delta) + ' s) and start'
                'update sessions cards at: ' + str(datetime.now()) + '')

        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text=text)

        self.stdout.write('sessions')
        s_update = []
        # sessions = Session.objects.filter(updated_at__gte=datetime.now().date)
        # s_update += list(sessions.values_list('id_parladata', flat=True))
        votes = Vote.objects.filter(updated_at__gt=lastVoteTime)
        s_update += list(votes.values_list('session__id_parladata', flat=True))
        ballots = Ballot.objects.filter(updated_at__gt=lastBallotTime)
        s_update += list(ballots.values_list('vote__session__id_parladata',
                                            flat=True))

        p_update = list(ballots.values_list("person__id_parladata", flat=True))

        #if s_update:
        #    runSettersSessions(sessions_ids=list(set(s_update)))

        t_delta = time() - start_time

        text = ('End creating cards (' + str(t_delta) + ' s) and start'
                'creating recache: ' + str(datetime.now()) + '')
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text=text)

        lockFile = open('parser.lock', 'w+')
        lockFile.write('UNLOCKED')
        lockFile.close()

        # recache

        # add sesessions of updated speeches to recache

        speeches = Speech.objects.filter(updated_at__gt=lastSpeechTime)

        s_update += list(speeches.values_list("session__id_parladata", flat=True))
        s_p_update = list(speeches.values_list("person__id_parladata", flat=True))

        date_ = (datetime.now() + timedelta(days=1)).strftime(API_DATE_FORMAT)
        if s_update:
            getSessionsList(None, date_, force_render=True)
        self.stdout.write(str(s_update))
        if s_update:
            self.stdout.write('recache')
            speech_the_order()
            deleteRendersOfSession(list(set(s_update)))
            refetch()

        p_update += list(speeches.values_list("person__id_parladata", flat=True))

        questions = Question.objects.filter(updated_at__gt=lastQustionTime)

        q_update = list(questions.values_list("person__id_parladata", flat=True))
        p_update += q_update

        # nightly update
        if not fast:
            # read draft legislations
            importDraftLegislationsFromFeed()
            # update last activites
            deleteRendersOfIDs(list(set(p_update)), 'p', 'zadnje-aktivnosti')
            deleteRendersOfIDs(list(set(q_update)), 'p', 'poslanska-vprasanja-in-pobude')
            deleteRendersOfIDs(list(set(s_p_update)), 'p', 'povezave-do-govorov')

            delete_renders(group='pg', method='poslanska-vprasanja-in-pobude')
            delete_renders(group='pg', method='vsi-govori-poslanske-skupine')

        t_delta = time() - start_time

        text = ('End fastUpdate everything (' + str(t_delta) + ' s): '
                '' + str(datetime.now()) + '')

        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text=text)
