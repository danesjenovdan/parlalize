import csv
from datetime import datetime
from parlaseje.models import Session
from parlalize.settings import API_URL, API_DATE_FORMAT
import requests
from collections import Counter
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, getScores, problematicno, privzdignjeno, preprosto, TFIDF, getCountList
from itertools import groupby


class WordAnalysis(object):
    date_ = None
    api_url = None
    date_of = None
    members = None
    membersOfPGsRanges = None
    count_of = "members"
    text = {}
    unique_words = []
    all_words = []
    swizec_coef = []
    average_words = None


    def __init__(self, api_url, count_of="members", date_=None):
        self.api_url = api_url
        if date_:
            self.date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
            self.date_ = date_
        else:
            self.date_of = datetime.now().date()
            self.date_=""

        self.count_of = count_of

        #get members for this day
        self.members = requests.get(self.api_url +'/getMPs/'+self.date_).json()
        self.allTimeMembers = requests.get(self.api_url +'/getAllTimeMemberships').json()
        self.prepereSpeeches()
        self.wordCounter()


    def prepereSpeeches(self):
        #prepare data for members
        if self.count_of == "members":
            for mp in self.members:
                print "[INFO] prepering data of member: " + str(mp['id'])
                speeches = requests.get(self.api_url +'/getSpeeches/' + str(mp['id']) + (("/"+self.date_) if self.date_ else "")).json()
                self.text[str(mp['id'])] = ''.join([speech['content'] for speech in speeches])
            print "[INFO] counting avg words of members"
            all_speeches = requests.get(API_URL+'/getAllSpeechesOfMPs/'+self.date_).json()
            text = ''.join([speech['content'] for speech in all_speeches])
            total_words = numberOfWords(text)
            self.average_words = total_words/len(self.allTimeMembers)

        #prepare data for groups
        elif self.count_of == "groups":
            self.membersOfPGsRanges = requests.get(API_URL+'/getMembersOfPGsRanges' + ("/"+self.date_ if self.date_ else "/")).json()
            print "[INFO] prepering data for groups: "
            for pgMembersRange in self.membersOfPGsRanges:
                print "___" + pgMembersRange["start_date"]
                for pg in pgMembersRange["members"].keys():
                    for member in pgMembersRange["members"][pg]: 
                        speeches = requests.get(API_URL+'/getSpeechesInRange/' + str(member) + "/" + pgMembersRange["start_date"] + "/" + pgMembersRange["end_date"]).json()
                        if pg in self.text.keys():
                            self.text[pg] += ''.join([speech['content'] for speech in speeches])
                        else:
                            self.text[pg] = ''.join([speech['content'] for speech in speeches])
            print "[INFO] counting avg words of groups"
            texts = ''.join(self.text.values())
            total_words = numberOfWords(texts)
            self.average_words = total_words/len(self.text.keys())

        
    def wordCounter(self):
        for counted_obj, words in self.text.items():
            print "[INFO] counting "+ self.count_of + ": " + str(counted_obj)
            
            #unique words
            unique = countWords(words, Counter())
            self.unique_words.append({'counter_id': counted_obj, 'vocabulary_size': len(unique)})
            
            #words count
            all_words_of_this = numberOfWords(words)
            self.all_words.append({'counter_id': counted_obj, 'wordcount': all_words_of_this})
            
            #swizec coeficient
            M1 = float(all_words_of_this)
            M2 = sum([len(list(g))*(freq**2) for freq,g in groupby(sorted(dict(unique).values()))])
            self.swizec_coef.append({'counter_id': counted_obj, 'coef': (M1*M1)/(M2-M1)})

        
    def getDate(self):
        return self.date_of

    #Vocabulary size
    def getVocabularySize(self):
        return self.swizec_coef

    def getMaxVocabularySize(self):
        vocabularies_sorted = sorted(self.swizec_coef, key=lambda k: k['coef'])
        maxMP = vocabularies_sorted[-1]['counter_id']
        return vocabularies_sorted[-1]['coef'], maxMP

    def getAvgVocabularySize(self):
        scores = [person['coef'] for person in self.swizec_coef]
        return float(sum(scores))/float(len(scores))

    #Spoken words
    def getSpokenWords(self):
        return self.all_words

    def getMaxSpokenWords(self):
        spoken_words_sorted = sorted(self.all_words, key=lambda k: k['wordcount'])
        maxMP = spoken_words_sorted[-1]['counter_id']
        return spoken_words_sorted[-1]['wordcount'], maxMP

    def getAvgSpokenWords(self):
        return self.average_words


class Utils(object):

    def getSpeechesAnalyses(self):
        with open('members_speech_score.csv', 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            date_ = "15.7.2016"
            mps = requests.get(API_URL+'/getMPs/'+date_).json()

            #NumberOfSpeechesPerSession
            mp_scores = {}

            for mp in mps:
                mp_no_of_speeches = len(requests.get(API_URL+'/getSpeechesOfMP/' + str(mp['id'])  + ("/"+date_) if date_ else "").json())

                # fix for "Dajem besedo"
                #mp_no_of_speeches = mp_no_of_speeches - int(requests.get(API_URL + '/getNumberOfFormalSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").text)

                mp_no_of_sessions = requests.get(API_URL+ '/getNumberOfPersonsSessions/' + str(mp['id']) + ("/"+date_) if date_ else "").json()['sessions_with_speech']

                if mp_no_of_sessions > 0:
                    mp_scores[mp['id']] = mp_no_of_speeches/mp_no_of_sessions
                else:
                    mp_scores[mp['id']] = 0
            print "NumberOfSpeechesPerSession done"

            #VocabularySize
            vocabulary_sizes = {}

            for mp in mps:

                speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").json()

                text = ''.join([speech['content'] for speech in speeches])

                vocabulary_sizes[mp['id']] = len(countWords(text, Counter()))

            print "VocabularySize done"

            #spoken words
            mp_results = {}

            for mp in mps:
                print '[INFO] Pasting speeches for MP ' + str(mp['id'])
                speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id']) + "/" + date_).json()

                text = ''.join([speech['content'] for speech in speeches])

                mp_results[mp['id']] = numberOfWords(text)

            print "spoken words done"

            for mp in mps:
                csvwriter.writerow([mp["id"], mp_results[mp['id']], vocabulary_sizes[mp['id']], mp_scores[mp['id']]])