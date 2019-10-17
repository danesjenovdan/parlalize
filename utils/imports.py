from parlalize.settings import API_URL, API_DATE_FORMAT, SETTER_KEY, PARSER_UN, PARSER_PASS, BASE_URL, DZ
from parlalize.utils_ import tryHard, getDataFromPagerApi, getDataFromPagerApiGen
from parlaposlanci.models import Person, District, MinisterStatic
from parlaskupine.models import Organization
from parlaseje.models import Session, Speech, Question, Ballot, Vote, Question, Tag, Legislation, AgendaItem, Debate
from django.test.client import RequestFactory
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from raven.contrib.django.raven_compat.models import client
from utils.parladata_api import getVotersIDs, getQuestions, getLinks, getPeople, getVotersPairsWithOrg, getOrganizations, getSpeeches, getBallots
from django.core.management import call_command

import requests
import re
import feedparser
# parlalize initial runner methods #

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

# TODO: do something with this method
def deleteUnconnectedSpeeches():
    idsInData = [speech['id'] for chunk in getSpeeches() for speech in chunk]
    blindSpeeches = Speech.objects.all().exclude(id_parladata__in=idsInData)
    blindSpeeches.delete()


# TODO check if is this necessary
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


# TODO check if is this necessary
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
    call_command('updateOrgs')
    print 'orgs done'

    print 'start people'
    call_command('updatePeople')
    print 'people done'


    print 'start sessions'
    #setAllSessions()
    call_command('setSessions')
    print 'Sessions done'

    print 'start speeches'
    updateSpeeches()
    call_command('my_command')

    print 'speeches done'

    print 'start votes'
    call_command('updateMotionOfSession')
    print 'votes done'

    print 'start ballots'
    call_command('updateBallots')
    print 'ballots done'

    print 'update districts and tags'
    call_command('updateDistricts')
    updateTags()
    call_command('updateTags')

    return 1


def importDraftLegislationsFromFeed():
    def split_epa_and_name(thing, date):
        print thing, date
        epa_regex = re.compile(r'\d+-(IX|IV|V?I{0,3})')
        current_epa = epa_regex.match(thing).group(0)
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
    # if update:
    #     exportLegislations()


def parse_for_notes():
    from bs4 import BeautifulSoup
    out = {}
    for vote in Vote.objects.all():
        print str(vote.id_parladata)
        url = 'https://glej.nov.parlameter.si/s/glasovanje/' + str(vote.id_parladata) + '?state=%7B%7D'
        soup = BeautifulSoup(requests.get(url).content)
        rich = soup.find("div", {"class": "rich-text"})
        if rich:
            text = rich.find("text-container")
            if text:
                out[str(vote.id_parladata)] = text.encode_contents()
    return out
