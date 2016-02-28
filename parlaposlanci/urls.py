from django.conf.urls import patterns, include, url
from parlaposlanci.views import *

urlpatterns = patterns(
    '',
#   url(r'^getMPsList/', getMPsList),

    # setters
    url(r'^setMPStatic/(?P<person_id>\d+)/', setMPStaticPL),

    url(r'^setMostEqualVoters/(?P<person_id>\d+)/', setMostEqualVoters),
    url(r'^setLeastEqualVoters/(?P<person_id>\d+)/', setLessEqualVoters),

    url(r'^setTFIDF/(?P<person_id>\d+)', setTFIDF),

    url(r'^setPresence/(?P<person_id>\d+)', setPercentOFAttendedSession),

    url(r'^setStyleScores/(?P<person_id>\d+)', setStyleScores),
    url(r'^setStyleScoresALL/', setStyleScoresALL),

    url(r'^setAverageNumberOfSpeechesPerSession/(?P<person_id>\d+)', setAverageNumberOfSpeechesPerSession),
    url(r'^setAverageNumberOfSpeechesPerSessionALL/', setAverageNumberOfSpeechesPerSessionAll),

    url(r'^setVocabularySize/(?P<person_id>\d+)', setVocabularySize),
    url(r'^setVocabularySizeALL/', setVocabularySizeALL),

    url(r'^setLastActivity/(?P<person_id>\d+)', setLastActivity),

    url(r'^setNumberOfSpokenWordsALL/', setNumberOfSpokenWordsALL),

    url(r'^setCutVotes/(?P<person_id>\d+)/(?P<date>[\w].+)', setCutVotes),
    url(r'^setCutVotes/(?P<person_id>\d+)', setCutVotes),


    ####################################################################################

    # getters
    url(r'^getMPStatic/(?P<person_id>\d+)/(?P<date>[\w].+)', getMPStaticPL),
    url(r'^getMPStatic/(?P<person_id>\d+)/', getMPStaticPL),

    url(r'^getMostEqualVoters/(?P<person_id>\d+)/(?P<date>[\w].+)', getMostEqualVoters),
    url(r'^getMostEqualVoters/(?P<person_id>\d+)/', getMostEqualVoters),

    url(r'^getLeastEqualVoters/(?P<person_id>\d+)/(?P<date>[\w].+)', getLessEqualVoters),
    url(r'^getLeastEqualVoters/(?P<person_id>\d+)/', getLessEqualVoters),

    url(r'^getTFIDF/(?P<person_id>\d+)/(?P<date>[\w].+)', getTFIDF),
    url(r'^getTFIDF/(?P<person_id>\d+)', getTFIDF),

    url(r'^getPresence/(?P<person_id>\d+)/(?P<date>[\w].+)', getPercentOFAttendedSession),
    url(r'^getPresence/(?P<person_id>\d+)', getPercentOFAttendedSession),

    url(r'^getStyleScores/(?P<person_id>\d+)/(?P<date>[\w].+)', getStyleScores),
    url(r'^getStyleScores/(?P<person_id>\d+)', getStyleScores),

    url(r'^getAverageNumberOfSpeechesPerSession/(?P<person_id>\d+)/(?P<date>[\w].+)', getAverageNumberOfSpeechesPerSession),
    url(r'^getAverageNumberOfSpeechesPerSession/(?P<person_id>\d+)', getAverageNumberOfSpeechesPerSession),

    url(r'^getNumberOfSpokenWords/(?P<person_id>\d+)/(?P<date>[\w].+)', getNumberOfSpokenWords),
    url(r'^getNumberOfSpokenWords/(?P<person_id>\d+)', getNumberOfSpokenWords),

    url(r'^getLastActivity/(?P<person_id>\d+)/(?P<date>[\w].+)', getLastActivity),
    url(r'^getLastActivity/(?P<person_id>\d+)', getLastActivity),

    url(r'^getVocabularySize/(?P<person_id>\d+)/(?P<date>[\w].+)', getVocabularySize),
    url(r'^getVocabularySize/(?P<person_id>\d+)', getVocabularySize),

    url(r'^getCutVotes/(?P<person_id>\d+)/(?P<date>[\w].+)', getCutVotes),
    url(r'^getCutVotes/(?P<person_id>\d+)', getCutVotes),

    url(r'^getAllSpeeches/(?P<person_id>\d+)/(?P<date>[\w].+)', getAllSpeeches),
    url(r'^getAllSpeeches/(?P<person_id>\d+)', getAllSpeeches),

    url(r'^getMPsIDs', getMPsIDs),

    url(r'^getCompass', getCompass),

    ####################################################################################

    #runenr
    url(r'^runSetters/(?P<date_to>[\w].+)', runSetters),
)
