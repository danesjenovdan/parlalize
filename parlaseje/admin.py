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

class LegislationNote(Legislation):
    class Meta:
        proxy = True

class VoteNotes(admin.ModelAdmin):
    search_fields = ['session__name', 'motion', 'abstractVisible']
    readonly_fields=('motion',)
    fields = ('motion', 'note', 'abstractVisible')

class LegislationNotes(admin.ModelAdmin):
    search_fields = ['text', 'abstractVisible']
    list_display = ('id',
                    'sessions_str',
                    'text',
                    'epa',
                    'date',
                    'status',
                    'result',
                    'has_note')

    list_editable = ('status', 'result')
    list_filter = ('result', 'status', 'date')
    readonly_fields=('text',)
    fields = ('text', 'status', 'result', 'note', 'abstractVisible')

    def has_note(self, obj):
        return bool(obj.note)

    def sessions_str(self, obj):
        return ', '.join(obj.sessions.all().values_list('name', flat=True))


admin.site.register(Session, SessionAdmin)
admin.site.register(VoteDetailed)
admin.site.register(Vote)
admin.site.register(VoteNote, VoteNotes)
admin.site.register(Legislation)
admin.site.register(LegislationNote, LegislationNotes)
admin.site.register(Activity)
admin.site.register(Speech)
admin.site.register(Ballot)
admin.site.register(AbsentMPs)
admin.site.register(Quote)
admin.site.register(PresenceOfPG)
admin.site.register(Tfidf, TFIDFAdmin)

