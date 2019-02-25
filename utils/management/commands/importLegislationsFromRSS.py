from django.core.management.base import BaseCommand, CommandError

from datetime import datetime
from parlaseje.models import Legislation

import requests
import feedparser
import re

class Command(BaseCommand):
    help = 'Import legislations from RSS feed'

    def handle(self, *args, **options):
        self.stdout.write('Import legislations from RSS feed')

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

        result = check_and_save_legislation(epas_and_names_tuple_zakoni, 'zakon')
        self.stdout.write(result)

        result = check_and_save_legislation(epas_and_names_tuple_akti, 'akt')
        self.stdout.write(result)

def split_epa_and_name(thing, date): 
    epa_regex = re.compile(r'\d+-VIII') 
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
    epa_regex = re.compile(r'\d+-VIII \w.+')
    result = epa_regex.findall(text)
    if result:
        return result[0]
    else:
        return None