import sys
from django.contrib import admin
from parlaseje.models import *
reload(sys)
sys.setdefaultencoding('utf-8')

# Register your models here.
admin.site.register(Session)
admin.site.register(Vote_graph)
admin.site.register(Vote)
admin.site.register(Activity)
admin.site.register(Speech)
admin.site.register(Ballot)
admin.site.register(AbsentMPs)
admin.site.register(Quote)
admin.site.register(PresenceOfPG)
admin.site.register(Tag)
admin.site.register(AverageSpeeches)
admin.site.register(Tfidf)
