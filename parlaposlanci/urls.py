from django.conf.urls import include, url
from django.conf import settings
from parlaposlanci.views import *

from rest_framework import routers
from .api import TFIDFView

router = routers.DefaultRouter()
router.register(r'tfidfs', TFIDFView)

urlpatterns = [
    # getters
    url(r'^getMPStatic/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMPStaticPL),
    url(r'^getMPStatic/(?P<person_id>\d+)/', getMPStaticPL),

    url(r'^getMostEqualVoters/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMostEqualVoters),
    url(r'^getMostEqualVoters/(?P<person_id>\d+)/', getMostEqualVoters),

    url(r'^getLeastEqualVoters/(?P<person_id>\d+)/(?P<date_>[\w].+)', getLessEqualVoters),
    url(r'^getLeastEqualVoters/(?P<person_id>\d+)/', getLessEqualVoters),

    url(r'^getTFIDF/(?P<person_id>\d+)/(?P<date_>[\w].+)', getTFIDF),
    url(r'^getTFIDF/(?P<person_id>\d+)', getTFIDF),

    url(r'^getPresence/(?P<person_id>\d+)/(?P<date>[\w].+)', getPercentOFAttendedSession),
    url(r'^getPresence/(?P<person_id>\d+)', getPercentOFAttendedSession),

    url(r'^getStyleScores/(?P<person_id>\d+)/(?P<date_>[\w].+)', getStyleScores),
    url(r'^getStyleScores/(?P<person_id>\d+)', getStyleScores),

    url(r'^getAverageNumberOfSpeechesPerSession/(?P<person_id>\d+)/(?P<date>[\w].+)', getAverageNumberOfSpeechesPerSession),
    url(r'^getAverageNumberOfSpeechesPerSession/(?P<person_id>\d+)', getAverageNumberOfSpeechesPerSession),

    url(r'^getNumberOfSpokenWords/(?P<person_id>\d+)/(?P<date>[\w].+)', getNumberOfSpokenWords),
    url(r'^getNumberOfSpokenWords/(?P<person_id>\d+)', getNumberOfSpokenWords),

    url(r'^getLastActivity/(?P<person_id>\d+)/(?P<date_>[\w].+)', getLastActivity),
    url(r'^getLastActivity/(?P<person_id>\d+)', getLastActivity),

    url(r'^getVocabularySize/(?P<person_id>\d+)/(?P<date_>[\w].+)', getVocabularySize),
    url(r'^getVocabularySize/(?P<person_id>\d+)', getVocabularySize),
    url(r'^getVocabularySizeLanding/(?P<date_>[\w].+)', getVocabolarySizeLanding),
    url(r'^getVocabularySizeLanding', getVocabolarySizeLanding),
    url(r'^getUniqueWordsLanding/(?P<date_>[\w].+)', getVocabolarySizeUniqueWordsLanding),
    url(r'^getUniqueWordsLanding/', getVocabolarySizeUniqueWordsLanding),

    url(r'^getAllSpeeches/(?P<person_id>\d+)/(?P<date_>[\w].+)', getAllSpeeches),
    url(r'^getAllSpeeches/(?P<person_id>\d+)', getAllSpeeches),

    url(r'^getQuestions/(?P<person_id>\d+)/(?P<date_>[\w].+)', getQuestions),
    url(r'^getQuestions/(?P<person_id>\d+)', getQuestions),

    url(r'^getPresenceThroughTime/(?P<person_id>\d+)/(?P<date_>[\w].+)', getPresenceThroughTime),
    url(r'^getPresenceThroughTime/(?P<person_id>\d+)', getPresenceThroughTime),

    url(r'^getListOfMembersTickers/(?P<date_>[\w].+)', getListOfMembersTickers, {'org_id': settings.DZ}),
    url(r'^getListOfMembersTickers/', getListOfMembersTickers, {'org_id': settings.DZ}),

    url(r'^getMPsIDs', getMPsIDs),

    url(r'^getCompass/(?P<date_>[\w].+)', getCompass, {'org_id': settings.DZ}),
    url(r'^getCompass', getCompass, {'org_id': settings.DZ}),

    url(r'^getTaggedBallots/(?P<person_id>\d+)/(?P<date_>[\w].+)', getTaggedBallots),
    url(r'^getTaggedBallots/(?P<person_id>\d+)', getTaggedBallots),

    url(r'^getMembershipsOfMember/(?P<person_id>\d+)/(?P<date>[\w].+)', getMembershipsOfMember),
    url(r'^getMembershipsOfMember/(?P<person_id>\d+)', getMembershipsOfMember),

    url(r'^getNumberOfQuestions/(?P<person_id>\d+)/(?P<date_>[\w].+)', getNumberOfQuestions),
    url(r'^getNumberOfQuestions/(?P<person_id>\d+)/', getNumberOfQuestions),

    url(r'^getNumberOfAmendmetsOfMember/(?P<person_id>\d+)/(?P<date_>[\w].+)', getNumberOfAmendmetsOfMember),
    url(r'^getNumberOfAmendmetsOfMember/(?P<person_id>\d+)/', getNumberOfAmendmetsOfMember),

    url(r'^getListOfMembers/(?P<date_>[\w].+)', getListOfMembers),
    url(r'^getListOfMembers/', getListOfMembers),

    url(r'^getMismatchWithPG/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMismatchWithPG),
    url(r'^getMismatchWithPG/(?P<person_id>\d+)/', getMismatchWithPG),

    url(r'^getAllActiveMembers/', getAllActiveMembers),

    url(r'^getSlugs/', getSlugs),

    ###########################################################################

    #runer
    #url(r'^runSetters/(?P<date_to>[\w].+)', runSetters),

    # drf
    url(r'^', include(router.urls)),
]
