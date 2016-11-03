from django.conf.urls import patterns, include, url
from parlaskupine.views import *


urlpatterns = patterns('',

#	url(r'^getMPsList/', getMPsList),
	
    # setters
    # TJ
    url(r'^setBasicInfOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setBasicInfOfPG),
    url(r'^setBasicInfOfPG/(?P<pg_id>\d+)', setBasicInfOfPG),

    url(r'^setPercentOFAttendedSessionPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setPercentOFAttendedSessionPG),
    url(r'^setPercentOFAttendedSessionPG/(?P<pg_id>\d+)', setPercentOFAttendedSessionPG),
    url(r'^setBasicInfOfPG/(?P<pg_id>\d+)', setBasicInfOfPG),
    url(r'^setPercentOFAttendedSessionPG/(?P<pg_id>\d+)', setPercentOFAttendedSessionPG),

    url(r'^setMPsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setMPsOfPG),
    url(r'^setMPsOfPG/(?P<pg_id>\d+)', setMPsOfPG),

    # TK
    url(r'^setMostMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setMostMatchingThem),
    url(r'^setMostMatchingThem/(?P<pg_id>\d+)', setMostMatchingThem),

    url(r'^setLessMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setLessMatchingThem),
    url(r'^setLessMatchingThem/(?P<pg_id>\d+)', setLessMatchingThem),

    url(r'^setDeviationInOrg/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setDeviationInOrg),
    url(r'^setDeviationInOrg/(?P<pg_id>\d+)', setDeviationInOrg),

    url(r'^setCutVotes/(?P<pg_id>\d+)/(?P<date_>[\w].+)', setCutVotes),
    url(r'^setCutVotes/(?P<pg_id>\d+)', setCutVotes),

    url(r'^setWorkingBodies/(?P<org_id>\d+)/(?P<date_>[\w].+)', setWorkingBodies),
    url(r'^setWorkingBodies/(?P<org_id>\d+)', setWorkingBodies),

    url(r'^setVocabularySizeALL/(?P<date_>[\w].+)', setVocabularySizeALL),
    url(r'^setVocabularySizeALL', setVocabularySizeALL),


    # getters
    # TJ
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),

    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getPercentOFAttendedSessionPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),

    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfPG),
    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)', getSpeechesOfPG),
    
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),

    url(r'^getMPsOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getMPsOfPG),
    url(r'^getMPsOfPG/(?P<pg_id>\d+)', getMPsOfPG),
    
    # TK
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getMostMatchingThem),
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/', getMostMatchingThem),

    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getLessMatchingThem),
    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/', getLessMatchingThem),

    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getDeviationInOrg),
    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/', getDeviationInOrg),

    url(r'^getCutVotes/(?P<pg_id>\d+)/(?P<date>[\w].+)', getCutVotes),
    url(r'^getCutVotes/(?P<pg_id>\d+)', getCutVotes),

    url(r'^getTaggedBallots/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getTaggedBallots),
    url(r'^getTaggedBallots/(?P<pg_id>\d+)', getTaggedBallots),

    url(r'^getVocabularySize/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getVocabularySize),
    url(r'^getVocabularySize/(?P<pg_id>\d+)', getVocabularySize),

    url(r'^getWorkingBodies/(?P<org_id>\d+)/(?P<date_>[\w].+)', getWorkingBodies),
    url(r'^getWorkingBodies/(?P<org_id>\d+)', getWorkingBodies),

    url(r'^getStyleScores/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getStyleScoresPG),
    url(r'^getStyleScores/(?P<pg_id>\d+)', getStyleScoresPG),

    url(r'^getPGsIDs', getPGsIDs),

    ####################################################################################

    # runenr
    #url(r'^runSetters/(?P<date_to>[\w].+)', runSetters),

    url(r'^getListOfPGs/(?P<date_>[\w].+)/', getListOfPGs),
    url(r'^getListOfPGs/', getListOfPGs),

    url(r'^getWorkingBodiesLive/(?P<org_id>\d+)/(?P<date_>[\w].+)', getWorkingBodies_live),
)
