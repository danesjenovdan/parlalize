import sys
from django.contrib import admin
from parlaseje.models import *
from .forms import LegislationForm


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
    list_display = ('id',
                    'motion',
                    'session',
                    'epa',
                    'start_time')

    list_filter = ('session__name', 'start_time', 'epa')
    readonly_fields=('motion',)
    fields = ('motion', 'note', 'abstractVisible')

class LegislationNotes(admin.ModelAdmin):
    form = LegislationForm
    search_fields = ['text', 'epa', 'sessions__name']
    list_display = ('id',
                    'sessions_str',
                    'text',
                    'epa',
                    'date',
                    'type_of_law',
                    'status',
                    'result',
                    'abstractVisible',
                    'mdt',
                    'is_exposed',
                    'icon',
                    'procedure_ended')

    list_editable = ('status', 'result', 'is_exposed')
    list_filter = ('result', 'status', 'date', 'is_exposed', 'result', 'procedure_ended')
    readonly_fields=('text',)
    #fields = ('text', 'status', 'result', 'note', 'abstractVisible', 'is_exposed', 'icon')

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

