import csv
from datetime import datetime
from parlaseje.models import Session
from parlalize.settings import API_URL, API_DATE_FORMAT, ISCI_URL
import requests
from collections import Counter
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, getScores, problematicno, privzdignjeno, preprosto, TFIDF, getCountList
from itertools import groupby

from parlalize.utils import tryHard

class WordAnalysis(object):
    def __init__(self, count_of="members", date_=None):
        self.date_ = ""
        self.api_url = None
        self.date_of = None
        self.members = None
        self.membersOfPGsRanges = None
        self.membersOfPGs = None
        self.count_of = "members"
        self.text = {}
        self.unique_words = []
        self.all_words = []
        self.swizec_coef = []
        self.average_words = None
        #API_URL = api_url
        if date_:
            self.date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
            self.date_ = date_
        else:
            self.date_of = datetime.now().date()
            self.date_=""

        self.isNewSpeech = tryHard(API_URL +'/isSpeechOnDay/'+self.date_).json()["isSpeech"]
        print self.isNewSpeech
        if self.isNewSpeech:
            self.count_of = count_of

            #get members for this day
            self.members = tryHard(API_URL +'/getMPs/'+self.date_).json()
            self.allTimeMembers = tryHard(API_URL +'/getAllTimeMemberships').json()
            #self.prepereSpeechesFromSearch()
            self.prepereSpeeches()
            self.wordCounter()

    def prepereSpeechesFromSearch(self):
        if self.count_of == "members":
            print "[INFO] [INFO] prepering data of members"
            for mp in self.members:
                print mp["id"]
                #unique words
                tfidf = tryHard(ISCI_URL + "/tfidfALL/p/" + str(mp['id']) + (("/"+self.date_) if self.date_ else "")).json()
                self.unique_words.append({'counter_id': str(mp['id']), 'unique': len(tfidf["results"])})

                #allWords
                all_words_of_this = sum([word["scores"]["tf"] for word in tfidf["results"]])
                self.all_words.append({'counter_id': str(mp['id']), 'wordcount': all_words_of_this})

                #swizec coeficient
                M1 = float(all_words_of_this)
                M2 = sum([freq ** 2 for freq in [tf["scores"]["tf"] for tf in tfidf["results"]]])
                #print M1, M2, "m1 pa m2"
                try:
                    self.swizec_coef.append({'counter_id': str(mp['id']), 'coef': (M1*M1)/(M2-M1)})
                except:
                    self.swizec_coef.append({'counter_id': str(mp['id']), 'coef': 0})

        elif self.count_of == "groups":
            print "[INFO] prepering data for groups: "
            self.membersOfPGs = tryHard(API_URL+'/getMembersOfPGsOnDate' + ("/"+self.date_ if self.date_ else "/")).json()
            allTimePGs = tryHard(API_URL+'/getAllPGsExt/').json().keys()
            for pg in self.membersOfPGs:
                if pg in allTimePGs and membersOfPGs[pg].members:
                    tfidf = tryHard(ISCI_URL+ "/tfidfALL/pg/" + str(pg) + (("/"+self.date_) if self.date_ else "")).json()
                    self.unique_words.append({'counter_id': str(mp['id']), 'unique': len(tfidf["results"])})
                    all_words_of_this = sum([word["scores"]["tf"] for word in tfidf["results"]])
                    self.all_words.append({'counter_id': counted_obj, 'wordcount': all_words_of_this})

                    #swizec coeficient
                    M1 = float(all_words_of_this)
                    M2 = sum([len(list(g))*(freq**2) for freq,g in groupby(sorted([tf["score"]["tf"] for tf in tfidf["results"]]))])
                    #print M1, M2, "m1 pa m2"
                    try:
                        self.swizec_coef.append({'counter_id': counted_obj, 'coef': (M1*M1)/(M2-M1)})
                    except:
                        self.swizec_coef.append({'counter_id': counted_obj, 'coef': 0})

    def prepereSpeeches(self):
        #prepare data for members
        if self.count_of == "members":
            print "[INFO] [INFO] prepering data of members"
            for mp in self.members:
                #print "[INFO] prepering data of member: " + str(mp['id'])
                url = API_URL +'/getSpeeches/' + str(mp['id']) + (("/"+self.date_) if self.date_ else "")
                speeches = tryHard(url).json()
                self.text[str(mp['id'])] = ''.join([speech['content'] for speech in speeches])
            print "[INFO] counting avg words of members"
            all_speeches = tryHard(API_URL+'/getAllMPsSpeeches/'+self.date_).json()
            text = ''.join([speech['content'] for speech in all_speeches])
            total_words = numberOfWords(text)
            self.average_words = total_words/len(self.allTimeMembers)

        #prepare data for groups
        elif self.count_of == "groups":
            self.membersOfPGsRanges = tryHard(API_URL+'/getMembersOfPGsRanges' + ("/"+self.date_ if self.date_ else "/")).json()
            print "[INFO] prepering data for groups: "
            for pgMembersRange in self.membersOfPGsRanges:
                #print "___" + pgMembersRange["start_date"]
                for pg in pgMembersRange["members"].keys():
                    for member in pgMembersRange["members"][pg]: 
                        speeches = tryHard(API_URL+'/getSpeechesInRange/' + str(member) + "/" + pgMembersRange["start_date"] + "/" + pgMembersRange["end_date"]).json()
                        if pg in self.text.keys():
                            self.text[pg] += ''.join([speech['content'] for speech in speeches])
                        else:
                            self.text[pg] = ''.join([speech['content'] for speech in speeches])
            print "[INFO] counting avg words of groups"
            texts = ''.join(self.text.values())
            total_words = numberOfWords(texts)
            self.average_words = total_words/len(self.text.keys())

        
    def wordCounter(self):
        print "[INFO] counting words"
        for counted_obj, words in self.text.items():
            #print "[INFO] counting "+ self.count_of + ": " + str(counted_obj), "words: ", len(words)
            
            #unique words
            unique = countWords(words, Counter())
            self.unique_words.append({'counter_id': counted_obj, 'unique': len(unique)})
            
            #words count
            all_words_of_this = numberOfWords(words)
            self.all_words.append({'counter_id': counted_obj, 'wordcount': all_words_of_this})
            
            #swizec coeficient
            M1 = float(all_words_of_this)
            M2 = sum([len(list(g))*(freq**2) for freq,g in groupby(sorted(dict(unique).values()))])
            #print M1, M2, "m1 pa m2"
            try:
                self.swizec_coef.append({'counter_id': counted_obj, 'coef': (M1*M1)/(M2-M1)})
            except:
                self.swizec_coef.append({'counter_id': counted_obj, 'coef': 0})

        
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

    #Unique words
    def getUniqueWords(self):
        return self.unique_words

    def getMaxUniqueWords(self):
        unique_sorted = sorted(self.unique_words, key=lambda k: k['unique'])
        maxMP = unique_sorted[-1]['counter_id']
        return unique_sorted[-1]['unique'], maxMP

    def getAvgUniqueWords(self):
        scores = [person['unique'] for person in self.unique_words]
        return float(sum(scores))/float(len(scores))

    #Spoken words
    def getSpokenWords(self):
        return self.all_words

    def getMaxSpokenWords(self):
        spoken_words_sorted = sorted(self.all_words, key=lambda k: k['wordcount'])
        maxMP = spoken_words_sorted[-1]['counter_id']
        return spoken_words_sorted[-1]['wordcount'], maxMP

    def getAvgSpokenWords(self):
        scores = [person['wordcount'] for person in self.all_words]
        return float(sum(scores))/float(len(scores))


class Utils(object):

    def getSpeechesAnalyses(self):
        with open('members_speech_score.csv', 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            date_ = "15.7.2016"
            mps = tryHard(API_URL+'/getMPs/'+date_).json()

            #NumberOfSpeechesPerSession
            mp_scores = {}

            for mp in mps:
                mp_no_of_speeches = len(tryHard(API_URL+'/getSpeechesOfMP/' + str(mp['id'])  + ("/"+date_) if date_ else "").json())

                # fix for "Dajem besedo"
                #mp_no_of_speeches = mp_no_of_speeches - int(tryHard(API_URL + '/getNumberOfFormalSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").text)

                mp_no_of_sessions = tryHard(API_URL+ '/getNumberOfPersonsSessions/' + str(mp['id']) + ("/"+date_) if date_ else "").json()['sessions_with_speech']

                if mp_no_of_sessions > 0:
                    mp_scores[mp['id']] = mp_no_of_speeches/mp_no_of_sessions
                else:
                    mp_scores[mp['id']] = 0
            print "NumberOfSpeechesPerSession done"

            #VocabularySize
            vocabulary_sizes = {}

            for mp in mps:

                speeches = tryHard(API_URL+'/getSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").json()

                text = ''.join([speech['content'] for speech in speeches])

                vocabulary_sizes[mp['id']] = len(countWords(text, Counter()))

            print "VocabularySize done"

            #spoken words
            mp_results = {}

            for mp in mps:
                #print '[INFO] Pasting speeches for MP ' + str(mp['id'])
                speeches = tryHard(API_URL+'/getSpeeches/' + str(mp['id']) + "/" + date_).json()

                text = ''.join([speech['content'] for speech in speeches])

                mp_results[mp['id']] = numberOfWords(text)

            print "spoken words done"

            for mp in mps:
                csvwriter.writerow([mp["id"], mp_results[mp['id']], vocabulary_sizes[mp['id']], mp_scores[mp['id']]])
