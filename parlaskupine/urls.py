from django.conf.urls import include, url
from django.conf import settings
from .views import *

from rest_framework import routers
from .api import TFIDFView

router = routers.DefaultRouter()
router.register(r'tfidfs', TFIDFView)


urlpatterns = [
    # setters

    url(r'^setWorkingBodies/(?P<org_id>\d+)/(?P<date_>[\w].+)', setWorkingBodies),
    url(r'^setWorkingBodies/(?P<org_id>\d+)', setWorkingBodies),

    # getters
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),

    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getPercentOFAttendedSessionPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),

    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfPG),
    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)', getSpeechesOfPG),

    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),

    url(r'^getMPsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getMPsOfPG),
    url(r'^getMPsOfPG/(?P<pg_id>\d+)', getMPsOfPG),

    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getMostMatchingThem),
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/', getMostMatchingThem),

    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getLessMatchingThem),
    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/', getLessMatchingThem),

    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getDeviationInOrg),
    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/', getDeviationInOrg),

    url(r'^getTaggedBallots/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getTaggedBallots),
    url(r'^getTaggedBallots/(?P<pg_id>\d+)', getTaggedBallots),

    url(r'^getVocabularySize/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getVocabularySize),
    url(r'^getVocabularySize/(?P<pg_id>\d+)', getVocabularySize),

    url(r'^getWorkingBodies/(?P<org_id>\d+)/(?P<date_>[\w].+)', getWorkingBodies),
    url(r'^getWorkingBodies/(?P<org_id>\d+)', getWorkingBodies),

    url(r'^getStyleScores/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getStyleScoresPG),
    url(r'^getStyleScores/(?P<pg_id>\d+)', getStyleScoresPG),

    url(r'^getTFIDF/(?P<party_id>\d+)/(?P<date_>[\w].+)', getTFIDF),
    url(r'^getTFIDF/(?P<party_id>\d+)', getTFIDF),

    url(r'^getNumberOfQuestions/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getNumberOfQuestions),
    url(r'^getNumberOfQuestions/(?P<pg_id>\d+)/', getNumberOfQuestions),

    url(r'^getQuestionsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getQuestionsOfPG),
    url(r'^getQuestionsOfPG/(?P<pg_id>\d+)/', getQuestionsOfPG),

    url(r'^getPresenceThroughTime/(?P<party_id>\d+)/(?P<date_>[\w].+)', getPresenceThroughTime),
    url(r'^getPresenceThroughTime/(?P<party_id>\d+)', getPresenceThroughTime),

    url(r'^getIntraDisunionOrg/(?P<org_id>\d+)', getIntraDisunionOrg),
    url(r'^getIntraDisunion/', getIntraDisunion),
    url(r'^getDisunionOrg/(?P<pg_id>\d+)', getDisunionOrgID),
    url(r'^getDisunionOrg/', getDisunionOrg),

    url(r'^getPGsIDs', getPGsIDs),

    url(r'^getAmendmentsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getAmendmentsOfPG),
    url(r'^getAmendmentsOfPG/(?P<pg_id>\d+)', getAmendmentsOfPG),

    url(r'^getNumberOfAmendmetsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getNumberOfAmendmetsOfPG),
    url(r'^getNumberOfAmendmetsOfPG/(?P<pg_id>\d+)', getNumberOfAmendmetsOfPG),

    url(r'^getPGMismatch/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getPGMismatch),
    url(r'^getPGMismatch/(?P<pg_id>\d+)/', getPGMismatch),


    ####################################################################################

    # runenr
    #url(r'^runSetters/(?P<date_to>[\w].+)', runSetters),

    url(r'^getListOfPGs/(?P<date_>[\w].+)/', getListOfPGs, {'organization_id': str(settings.DZ)}),
    url(r'^getListOfPGs/', getListOfPGs, {'organization_id': str(settings.DZ)}),

    url(r'^getWorkingBodiesLive/(?P<org_id>\d+)/(?P<date_>[\w].+)', getWorkingBodies_live),

    # drf
    url(r'^', include(router.urls)),

]
