import csv
from datetime import datetime
from parlaseje.models import Session
from parlalize.settings import API_URL
import requests
from collections import Counter
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, getScores, problematicno, privzdignjeno, preprosto, TFIDF, getCountList

def getSpeechesAnalyses():
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