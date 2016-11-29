from django.contrib import admin
import sys
from parlaposlanci.models import *
reload(sys)
sys.setdefaultencoding('utf-8')
# Register your models here.

class PersonAdmin(admin.ModelAdmin):
    search_fields = ['name']
    
admin.site.register(Person, PersonAdmin)
admin.site.register(Presence)
admin.site.register(SpokenWords)
admin.site.register(SpeakingStyle)
admin.site.register(CutVotes)
admin.site.register(LastActivity)
admin.site.register(EqualVoters)
admin.site.register(LessEqualVoters)
admin.site.register(MPStaticPL)
admin.site.register(NumberOfSpeechesPerSession)
admin.site.register(VocabularySize)
admin.site.register(VocabularySizeUniqueWords)
admin.site.register(StyleScores)
admin.site.register(Tfidf)
admin.site.register(AverageNumberOfSpeechesPerSession)
admin.site.register(Compass)
admin.site.register(TaggedBallots)
admin.site.register(MembershipsOfMember)
admin.site.register(District)




