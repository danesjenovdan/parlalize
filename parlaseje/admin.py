import sys
from django.contrib import admin
from parlaseje.models import *

reload(sys)
sys.setdefaultencoding('utf-8')


class SessionAdmin(admin.ModelAdmin):
    search_fields = ['name']


class TFIDFAdmin(admin.ModelAdmin):
    search_fields = ['session__name']

class VoteNote(Vote):
    class Meta:
        proxy = True

class VoteNotes(admin.ModelAdmin):
    search_fields = ['session__name', 'motion']
    readonly_fields=('motion',)
    fields = ('motion', 'note')


admin.site.register(Session, SessionAdmin)
admin.site.register(VoteDetailed)
admin.site.register(Vote)
admin.site.register(VoteNote, VoteNotes)
admin.site.register(Activity)
admin.site.register(Speech)
admin.site.register(Ballot)
admin.site.register(AbsentMPs)
admin.site.register(Quote)
admin.site.register(PresenceOfPG)
admin.site.register(Tfidf, TFIDFAdmin)

