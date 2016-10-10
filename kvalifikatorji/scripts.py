#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import slopos, nltk
from nltk.tokenize import word_tokenize
from string import maketrans, punctuation
from collections import Counter
import lemmagen.lemmatizer
from lemmagen.lemmatizer import Lemmatizer
from math import log
import tfidf
from itertools import repeat

import requests

def getWords(filename):
    f = open(filename, 'r')
    return f.read().splitlines()

def getWordsDict(filename):
    wordslist = getWords(filename)
    wordsdict = {word: 1 for word in wordslist}

    return wordsdict

problematicno = getWordsDict('kvalifikatorji/problematicno.txt')
privzdignjeno = getWordsDict('kvalifikatorji/privzdignjeno.txt')
preprosto = getWordsDict('kvalifikatorji/preprosto.txt')

text = 'Tudi v Poslanski skupini Socialnih demokratov ne bomo podprli proračunov za leti 2013 in 2014. Že v uvodnem nagovoru v imenu poslanske skupine smo opozorili, da ta dva proračuna nista odgovor na dogajanje v Sloveniji. Ljudje pričakujejo, da bosta ta dva proračuna omogočala gospodarski razvoj, da bosta omogočala zagotavljanje novih delovnih mest, da bosta omogočala nadaljnji obstoj in razvoj javnega šolstva, tako osnovnega kot tudi do nivoja univerz, in predvsem da bomo imeli vsi tudi temu primerno socialno varnost. Vseh teh problemov ta dva proračuna ne odpravljata, nasprotno. Kaže se, da vladajoča koalicija razume in sledi samo cilju čimprejšnje razprodaje državnega premoženja in želi pri tem omogočiti vsem tistim, ki imajo te informacije, da se vključijo v ta proces na način, da dajo prioriteto osebnim interesom, ne pa interesom države, ne interesom ljudi, ki pričakujejo, da bomo ravnali po našem mnenju, tudi v Državnem zboru, povsem drugače kot je zapisano v teh dveh proračunih.'

def numberOfWords(text):
    exclude = set(punctuation)
    text_lower = text.lower()
    text_nopunct_lower = ''.join(ch for ch in text_lower if ch not in exclude)
    return len(word_tokenize(text_nopunct_lower))

def lemmatizeTokens(tokens):

    lemmatized_tokens = []
    lemmatizer = Lemmatizer(dictionary=lemmagen.DICTIONARY_SLOVENE)

    for token in tokens:
        lemmatized_tokens.append(lemmatizer.lemmatize(token))

    return lemmatized_tokens

def countWords(text, counter):

    exclude = set(punctuation)
    text_lower = text.lower()
    text_nopunct_lower = ''.join(ch for ch in text_lower if ch not in exclude)

    tokens = lemmatizeTokens(word_tokenize(text_nopunct_lower))
    new_count = Counter(tokens)
    counter.update(new_count)

    return counter

def getCountList(speaker_id, date_):
    data = requests.get('https://isci.parlameter.si/tfidfALL/p/' + str(speaker_id) + "/" + date_).json()

    wordlist = data['results']

    wordlist_new = {word["term"]: word["scores"]["tf"] for word in wordlist}

    return wordlist_new

def getCountListPG(party_id, date_):
    data = requests.get('https://isci.parlameter.si/tfidfALL/ps/' + str(party_id) + "/" + date_).json()

    wordlist = data['results']

    wordlist_new = {word["term"]: word["scores"]["tf"] for word in wordlist}

    return wordlist_new

def getScore(words, counter, total):

    print 'Getting style scores'

    score = 0.0
#    lemmatized_words = lemmatizeTokens(words)
    lemmatized_words = words

    for word in counter:
        if word in lemmatized_words:
            score = (score + counter[word])

    return score/total

def getScores(words_list, counter, total):

    print 'Getting style scores'

    scores = {'problematicno': 0, 'privzdignjeno': 0, 'preprosto': 0}

    for word in counter:
        scores['problematicno'] = scores['problematicno'] + words_list[0].setdefault(word, 0)
        scores['privzdignjeno'] = scores['privzdignjeno'] + + words_list[1].setdefault(word, 0)
        scores['preprosto'] = scores['preprosto'] + + words_list[2].setdefault(word, 0)

    if float(total) == 0.0:
        total = 1

    scores['problematicno'] = scores['problematicno']/float(total)
    scores['privzdignjeno'] = scores['privzdignjeno']/float(total)
    scores['preprosto'] = scores['preprosto']/float(total)

    return scores

def TFIDF(speeches_grouped, person_id):

    # make documents
    documents = []
    for group in speeches_grouped:
        subdocuments = [speech['content'] for speech in group['speeches']]
        document = ''.join(subdocuments)
        documents.append({'person_id': group['person_id'], 'document': document})

    # calculate term frequency for individual documents
    document_frequencies = []
    for document in documents:
        document_counter = Counter()
        document_frequencies.append({'person_id': document['person_id'], 'frequencies': countWords(document['document'], document_counter)})

    # calculate term frequency for the corpus
    corpus = ''.join([document['document'] for document in documents])
    corpus_tf = Counter()
    corpus_tf = countWords(corpus, corpus_tf)

    # other implementation
#    table = tfidf.tfidf()
#    for document in document_frequencies:
#        table.addDocument(str(document['person_id']), [x for item in document['frequencies'].keys() for x in repeat(item, document['frequencies'][item])])

    results = {}

    for document in document_frequencies:

        results[document['person_id']] = []

        max_frequency = 0
        for term in document['frequencies']:
            if document['frequencies'][term] > max_frequency:
                max_frequency = document['frequencies'][term]

        for term in document['frequencies']:
            idf = log(float(1 + len(documents)) / float(1 + corpus_tf[term]))
            tfidf = float(document['frequencies'][term]) / float(max_frequency) * float(idf)
            results[document['person_id']].append({'term': term, 'tfidf': tfidf})

    # sort results
    sorted_results = sorted(results[int(person_id)], key=lambda k: k['tfidf'], reverse=True)

    return sorted_results
#    return table.similarities(['delfin', 'tovariš'])
