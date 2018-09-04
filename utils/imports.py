from parlalize.settings import API_URL, API_DATE_FORMAT, SETTER_KEY, PARSER_UN, PARSER_PASS, BASE_URL
from parlalize.utils_ import tryHard, getDataFromPagerApi, getDataFromPagerApiGen
from parlaposlanci.models import Person, District, MinisterStatic
from parlaskupine.models import Organization
from parlaposlanci.views import setMinsterStatic
from parlaseje.models import Session, Speech, Question, Ballot, Vote, Question, Tag, Legislation
from parlaseje.views import setMotionOfSession
from .exports import exportLegislations
from django.test.client import RequestFactory
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from raven.contrib.django.raven_compat.models import client

import requests
import re
import feedparser
# parlalize initial runner methods #

DZ = 95
factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)


def updatePeople():
    url = API_URL + '/getAllPeople/'
    data = getDataFromPagerApi(url)
    mps = tryHard(API_URL + '/getMPs/').json()
    mps_ids = [mp['id'] for mp in mps]
    for mp in data:
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
            is_active = True if int(mp['id']) in mps_ids else False
            person = Person(name=mp['name'],
                            pg=mp['membership'],
                            id_parladata=int(mp['id']),
                            image=mp['image'],
                            actived=is_active,
                            gov_id=mp['gov_id'])
            person.save()

    return 1


def updateOrganizations(dummy_arg=None):
    data = tryHard(API_URL + '/getAllOrganizations').json()
    for pg in data:
        if Organization.objects.filter(id_parladata=pg):
            org = Organization.objects.get(id_parladata=pg)
            org.name = data[pg]['name']
            org.classification = data[pg]['classification']
            org.acronym = data[pg]['acronym']
            org.is_coalition = data[pg]['is_coalition']
            print data[pg]['acronym']
            org.save()
        else:
            org = Organization(name=data[pg]['name'],
                               classification=data[pg]['classification'],
                               id_parladata=pg,
                               acronym=data[pg]['acronym'],
                               is_coalition=data[pg]['is_coalition'])
            org.save()
    return 1


def deleteUnconnectedSpeeches():
    url = API_URL + '/getAllSpeeches'
    data = getDataFromPagerApi(url)
    idsInData = [speech['id'] for speech in data]
    blindSpeeches = Speech.objects.all().exclude(id_parladata__in=idsInData)
    blindSpeeches.delete()


def updateSpeeches():
    url = API_URL + '/getAllAllSpeeches'
    existingISs = list(Speech.objects.all().values_list('id_parladata',
                                                        flat=True))
    for page in getDataFromPagerApiGen(url):
        for dic in page:
            if int(dic['id']) not in existingISs:
                print 'adding speech'
                print dic['valid_to']
                person = Person.objects.get(id_parladata=int(dic['speaker']))
                speech = Speech(organization=Organization.objects.get(
                                    id_parladata=int(dic['party'])),
                                content=dic['content'],
                                order=dic['order'],
                                agenda_item_order=dic['agenda_item_order'],
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
                print 'update speech'
                speech = Speech.objects.filter(id_parladata=dic['id'])
                speech.update(valid_from=dic['valid_from'],
                              valid_to=dic['valid_to'],
                              agenda_item_order=dic['agenda_item_order'])

    # delete speeches which was deleted in parladata @dirty fix
    #deleteUnconnectedSpeeches()
    return 1


def updateQuestions():
    url = API_URL + '/getAllQuestions'
    data = getDataFromPagerApi(url)
    existingISs = list(Question.objects.all().values_list("id_parladata",
                                                          flat=True))
    for dic in data:
        if int(dic["id"]) not in existingISs:
            print "adding question"
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
                static = MinisterStatic.objects.filter(person__id=post['membership__person_id'],
                                                       ministry=post['organization_id'])
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
            print(author_orgs)
            question.author_org.add(*author_org)
            question.person.add(*person)
            question.recipient_persons.add(*rec_p)
            question.recipient_organizations.add(*rec_org)
            question.recipient_persons_static.all(*rec_posts)
        else:
            print "update question"
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
            question = Question.objects.get(id_parladata=dic["id"])
            question.save()
            question.author_org.add(*author_org)
            question.person.add(*person)
            question.recipient_persons.add(*rec_p)
            question.recipient_organizations.add(*rec_org)
            question.recipient_persons_static.add(*rec_posts)

    return 1

# treba pofixsat


def updateMotionOfSession():
    ses = Session.objects.all()
    for s in ses:
        print s.id_parladata
        resp =  setMotionOfSession(request_with_key, str(s.id_parladata))
        print resp.content
        #tryHard(BASE_URL + '/s/setMotionOfSession/' + str(s.id_parladata) + '?key=' + SETTER_KEY )

# treba pofixsat


def updateBallots():
    url = (API_URL + '/getAllBallots')
    data = getDataFromPagerApi(url)
    existingISs = Ballot.objects.all().values_list('id_parladata', flat=True)
    for dic in data:
        # Ballot.objects.filter(id_parladata=dic['id']):
        if int(dic['id']) not in existingISs:
            print 'adding ballot ' + str(dic['vote'])
            vote = Vote.objects.get(id_parladata=dic['vote'])
            person = Person.objects.get(id_parladata=int(dic['voter']))
            ballots = Ballot(option=dic['option'],
                             vote=vote,
                             start_time=vote.start_time,
                             end_time=None,
                             id_parladata=dic['id'])
            ballots.save()
            ballots.person.add(person)
    return 1


def setAllSessions():
    data = tryHard(API_URL + '/getSessions/').json()
    session_ids = list(Session.objects.all().values_list('id_parladata',
                                                         flat=True))
    for session in data:
        print session['id']
        orgs = Organization.objects.filter(id_parladata__in=session['organizations_id'])
        if not orgs:
            orgs = Organization.objects.filter(id_parladata=session['organization_id'])
        if session['id'] not in session_ids:
            result = Session(name=session['name'],
                             gov_id=session['gov_id'],
                             start_time=session['start_time'],
                             end_time=session['end_time'],
                             classification=session['classification'],
                             id_parladata=session['id'],
                             in_review=session['is_in_review'],
                             organization=orgs[0]
                             )
            result.save()
            orgs = list(orgs)
            result.organizations.add(*orgs)
            if session['id'] == DZ:
                if 'redna seja' in session['name'].lower():
                    # call method for create new list of members
                    # setListOfMembers(session['start_time'])
                    pass
        else:
            ses = Session.objects.filter(name=session['name'],
                                         gov_id=session['gov_id'],
                                         start_time=session['start_time'],
                                         end_time=session['end_time'],
                                         classification=session['classification'],
                                         id_parladata=session['id'],
                                         in_review=session['is_in_review'],
                                         organization=orgs[0])
            ses = ses.exclude(organizations=None)
            if not session:
                # save changes
                session2 = Session.objects.get(id_parladata=session['id'])
                session2.name = session['name']
                session2.gov_id = session['gov_id']
                session2.start_time = session['start_time']
                session2.end_time = session['end_time']
                session2.classification = session['classification']
                session2.in_review = session['is_in_review']
                session2.organization = orgs[0]
                session2.save()
                orgs = list(orgs)
                session2.organizations.add(*orgs)

    return 1


def updateMinistrers():
    ministers = tryHard(API_URL + '/getIDsOfAllMinisters/').json()['ministers_ids']
    for ministr in ministers:
        print ministr
        setMinsterStatic(request_with_key, str(ministr))


def updateDistricts():
    districts = tryHard(API_URL + '/getDistricts').json()
    existing_districts = District.objects.all().values_list('id_parladata',
                                                            flat=True)
    for district in districts:
        if district['id'] not in existing_districts:
            District(name=district['name'], id_parladata=district['id']).save()
        else:
            dist = District.objects.get(id_parladata=district['id'])
            if dist.name != district['name']:
                dist.name = district['name']
                dist.save()
    return 1


def updateTags():
    tags = tryHard(API_URL+'/getTags').json()
    existing_tags = Tag.objects.all().values_list('id_parladata', flat=True)
    count = 0
    for tag in tags:
        if tag['id'] not in existing_tags:
            Tag(name=tag['name'], id_parladata=tag['id']).save()
            count += 1
    return 1


def updatePersonStatus():
    mps = tryHard(API_URL + '/getMPs').json()
    mps_ids = [mp['id'] for mp in mps]
    for person in Person.objects.all():
        if person.actived == 'Yes':
            if person.id_parladata not in mps_ids:
                person.actived = 'No'
                person.save()
        else:
            if person.id_parladata in mps_ids:
                person.actived = 'Yes'
                person.save()


def updatePersonFunctions():
    mps = tryHard(API_URL + '/getMembersWithFunction/').json()

    for person in Person.objects.all():
        if person.has_function:
            if person.id_parladata not in mps['members_with_function']:
                person.has_function = False
                person.save()
        else:
            if person.id_parladata in mps['members_with_function']:
                person.has_function = True
                person.save()


def update():
    updateOrganizations()
    print 'orgs done'

    print 'start people'
    updatePeople()
    print 'people done'

    print 'start ministers'
    updateMinistrers()
    print 'ministers done'

    print 'start sessions'
    setAllSessions()
    print 'Sessions done'

    print 'start speeches'
    updateSpeeches()
    print 'speeches done'

    print 'start votes'
    updateMotionOfSession()
    print 'votes done'

    print 'start ballots'
    updateBallots()
    print 'ballots done'

    print 'update districts and tags'
    updateDistricts()
    updateTags()

    print 'start update person status'
    updatePersonStatus()
    print 'update person status done'

    print 'start update person has_function'
    updatePersonFunctions()
    print 'update person has_function done'

    return 1


def updateLegislation(request):
    allLaws = []
    epas = []
    laws = requests.get(API_URL + '/law/',
                       auth=HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
    count = 144
    while laws['next'] != None:
        
        laws = requests.get(API_URL + '/law/?page=' + str(count),
                            auth=HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
        for law in laws['results']:
            epas.append(str(law['epa']))
        count = count + 1
    for epa in set(epas):
        laws = requests.get(API_URL + '/law?epa=' + str(epa),
                        auth=HTTPBasicAuth(PARSER_UN, PARSER_PASS)).json()
        if int(laws['count']) > 1:
            for law in laws['results']:
                sorted_date = sorted(laws['results'], key=lambda x: datetime.strptime(x['date'].split('T')[0], '%Y-%m-%d'))
                print sorted_date[0]
                result = Legislation(#session=Session.objects.get(id_parladata=int(law['session'])),
                                       text=sorted_date['text'],
                                       epa=sorted_date['epa'],
                                       mdt=sorted_date['mdt'],
                                       proposer_text=sorted_date['proposer_text'],
                                       procedure_phase=sorted_date['procedure_phase'],
                                       procedure=sorted_date['procedure'],
                                       type_of_law=sorted_date['type_of_law'],
                                       mdt_fk=sorted_date['mdt_fk']
                                       )      
                result.save()
        else:
            result = Legislation(#session=Session.objects.get(id_parladata=int(law['session'])),
                                       text=laws['results']['text'],
                                       epa=laws['results']['epa'],
                                       mdt=laws['results']['mdt'],
                                       proposer_text=laws['results']['proposer_text'],
                                       procedure_phase=laws['results']['procedure_phase'],
                                       procedure=laws['results']['procedure'],
                                       type_of_law=laws['results']['type_of_law'],
                                       mdt_fk=laws['results']['mdt_fk']
                                       )      
            result.save()


def importDraftLegislationsFromFeed(): 
    def split_epa_and_name(thing, date): 
        epa_regex = re.compile(r'\d+-VII') 
        current_epa = epa_regex.findall(thing)[0] 
        current_name = thing.split(current_epa)[1].strip()
        date = getDate(date)
        return (current_epa, current_name, date)

    def check_and_save_legislation(legislations, classification):
        stats = {'saved': 0,
                 'skiped': 0}
        for legislation in legislations:
            saved = Legislation.objects.filter(epa=legislation[0])
            if not saved:
                Legislation(epa=legislation[0], text=legislation[1], date=legislation[2], classification=classification).save()
                stats['saved'] += 1
            else:
                stats['skiped'] += 1
        return stats

    def getDate(dat):
        return datetime.strptime(dat.split(',')[1].strip(), "%d %b %Y %X %Z")

    def getEpaFromText(text):
        epa_regex = re.compile(r'\d+-VII \w.+')
        result = epa_regex.findall(text)
        if result:
            return result[0]
        else:
            return None

    url_zakoni = 'https://www.dz-rs.si/DZ-LN-RSS/RSSProvider?rss=zak'
    url_akti = 'https://www.dz-rs.si/DZ-LN-RSS/RSSProvider?rss=akt'
    
    # najprej epe od zakonov 
    feed_zakoni = feedparser.parse(url_zakoni)
    epas_and_names_zakoni = list([(getEpaFromText(post.title), post['published']) for post in feed_zakoni.entries if getEpaFromText(post.title)])
    epas_and_names_tuple_zakoni = [split_epa_and_name(thing[0], thing[1]) for thing in epas_and_names_zakoni]

    # potem epe od aktov 
    feed_akti = feedparser.parse(url_akti)
    epas_and_names_akti = list([(getEpaFromText(post.title), post['published']) for post in feed_akti.entries  if getEpaFromText(post.title)])
    epas_and_names_tuple_akti = [split_epa_and_name(thing[0], thing[1]) for thing in epas_and_names_akti]

    update = False
    report = check_and_save_legislation(epas_and_names_tuple_zakoni, 'zakon')
    print report, 'zakon'
    if report['saved']:
        update = True
    report = check_and_save_legislation(epas_and_names_tuple_akti, 'akt')
    print report, 'akti'
    if report['saved']:
        update = True
    if update:
        exportLegislations()