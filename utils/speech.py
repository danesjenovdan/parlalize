import csv
from datetime import datetime
from parlaseje.models import Session, Activity
from parlaskupine.models import Organization
from parlalize.settings import API_DATE_FORMAT, ISCI_URL
from collections import Counter
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, getScores, problematicno, privzdignjeno, preprosto, getCountList
from itertools import groupby

from parlalize.utils_ import tryHard, getDataFromPagerApi, getDataFromPagerApiDRFGen
from utils.parladata_api import getVotersIDs, getOrganizationsWithVoters, getSpeechContentOfPerson, getSpeeches


class WordAnalysis(object):
    def __init__(self, organization_id, count_of='members', date_=None):
        self.date_ = ''
        self.api_url = None
        self.date_of = None
        self.members = None
        self.membersOfPGsRanges = None
        self.membersOfPGs = None
        self.count_of = 'members'
        self.text = {}
        self.unique_words = []
        self.all_words = []
        self.swizec_coef = []
        self.average_words = None
        if date_:
            self.date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
            self.date_ = date_
        else:
            self.date_of = datetime.now().date()
            self.date_ = ''

        self.count_of = count_of

        # get members for this day

        self.members = getVotersIDs(organization_id=organization_id, date_=self.date_of)
        self.organizations = getOrganizationsWithVoters(organization_id=organization_id, date_=self.date_of)

        self.prepereSpeeches()
        self.wordCounter()

    def prepereSpeeches(self):
        # prepare data for members
        if self.count_of == 'members':
            print('[INFO] [INFO] prepering data of members')
            for mp in self.members:
                self.text[str(mp)] = ''
                for speechs_chunk in getSpeeches(speaker=mp, valid=True):
                    self.text[str(mp)] += ' '.join([speech['content'] for speech in speechs_chunk])

        # prepare data for groups
        elif self.count_of == 'groups':
            print('[INFO] prepering data for groups: ')
            for org_id in self.organizations:
                org = Organization.objects.filter(id_parladata=org_id).exclude(classification='unaligned MP')
                if org:
                    self.text[org_id] = ''
                    for speechs_chunk in getSpeeches(party=org_id, valid=True):
                        self.text[org_id] += ' '.join([speech['content'] for speech in speechs_chunk])

    def wordCounter(self):
        print('[INFO] counting words')
        for counted_obj, words in self.text.items():

            # unique words
            unique = countWords(words, Counter())
            self.unique_words.append({'counter_id': counted_obj,
                                      'unique': len(unique)})

            # words count
            all_words_of_this = numberOfWords(words)
            self.all_words.append({'counter_id': counted_obj,
                                   'wordcount': all_words_of_this})

            # swizec coeficient
            M1 = float(all_words_of_this)
            M2 = sum([len(list(g))*(freq**2)
                      for freq, g
                      in groupby(sorted(dict(unique).values()))])
            # print M1, M2, 'm1 pa m2'
            try:
                self.swizec_coef.append({'counter_id': counted_obj,
                                         'coef': (M1*M1)/(M2-M1)})
            except:
                self.swizec_coef.append({'counter_id': counted_obj,
                                         'coef': 0})

    def getDate(self):
        return self.date_of

    # Vocabulary size
    def getVocabularySize(self):
        return self.swizec_coef

    def getMaxVocabularySize(self):
        vocabularies_sorted = sorted(self.swizec_coef, key=lambda k: k['coef'])
        maxMP = vocabularies_sorted[-1]['counter_id']
        return vocabularies_sorted[-1]['coef'], maxMP

    def getAvgVocabularySize(self):
        scores = [person['coef'] for person in self.swizec_coef]
        return float(sum(scores))/float(len(scores))

    # Unique words
    def getUniqueWords(self):
        return self.unique_words

    def getMaxUniqueWords(self):
        unique_sorted = sorted(self.unique_words, key=lambda k: k['unique'])
        maxMP = unique_sorted[-1]['counter_id']
        return unique_sorted[-1]['unique'], maxMP

    def getAvgUniqueWords(self):
        scores = [person['unique'] for person in self.unique_words]
        return float(sum(scores))/float(len(scores))

    # Spoken words
    def getSpokenWords(self):
        return self.all_words

    def getMaxSpokenWords(self):
        spoken_words_sorted = sorted(self.all_words,
                                     key=lambda k: k['wordcount'])
        maxMP = spoken_words_sorted[-1]['counter_id']
        return spoken_words_sorted[-1]['wordcount'], maxMP

    def getAvgSpokenWords(self):
        scores = [person['wordcount'] for person in self.all_words]
        return float(sum(scores))/float(len(scores))


class Utils(object):
    def getSpeechesAnalyses(self, organization_id):
        with open('members_speech_score.csv', 'wb') as csvfile:
            csvwriter = csv.writer(csvfile,
                                   delimiter=',',
                                   quotechar='|',
                                   quoting=csv.QUOTE_MINIMAL)

            date_of = datetime.now().date()
            mps = getVotersIDs(date_=date_of, organization_id=organization_id)

            # NumberOfSpeechesPerSession
            mp_scores = {}

            for mp in mps:
                mp_no_of_speeches = len(getSpeechContentOfPerson(person_id, fdate=date_of))

                mp_no_of_sessions = Activity.objects.filter(
                    person__id_parladata=mp,
                    speech__isnull=False).distinct("session").count()

                if mp_no_of_sessions > 0:
                    mp_scores[mp] = mp_no_of_speeches/mp_no_of_sessions
                else:
                    mp_scores[mp] = 0
            print('NumberOfSpeechesPerSession done')

            # VocabularySize
            vocabulary_sizes = {}
            mp_results = {}

            for mp in mps:
                text =  ' '.join(getSpeechContentOfPerson(mp, fdate=date_of))

                vocabulary_sizes[mp] = len(countWords(text, Counter()))
                mp_results[mp] = numberOfWords(text)

            print('VocabularySize done')
            print('spoken words done')

            for mp in mps:
                csvwriter.writerow([mp,
                                   mp_results[mp],
                                   vocabulary_sizes[mp],
                                   mp_scores[mp]])
