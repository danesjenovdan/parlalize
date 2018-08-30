import sys
from django.contrib import admin
from parlaseje.models import *
from .forms import LegislationForm
import re


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
    def save_model(self, request, obj, form, change):
        clean_abstract(obj)
        super(VoteNotes, self).save_model(request, obj, form, change)

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
    def save_model(self, request, obj, form, change):
        clean_abstract(obj)
        super(LegislationNotes, self).save_model(request, obj, form, change)

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

    list_editable = ('status', 'result', 'is_exposed', 'procedure_ended')
    list_filter = ('result', 'status', 'date', 'is_exposed', 'result', 'procedure_ended')
    #readonly_fields=('text',)
    #fields = ('text', 'status', 'result', 'note', 'abstractVisible', 'is_exposed', 'icon')

    def sessions_str(self, obj):
        return ', '.join(obj.sessions.all().values_list('name', flat=True))

def clean_abstract(l):
    spanre = re.compile('<span.*?>')
    closespanre = re.compile(r'<\/span>')
    stylere = re.compile('style=".*?"')

    if l.note:
        l.note = spanre.sub('', l.note)
        l.note = closespanre.sub('', l.note)
        l.note = stylere.sub('', l.note)
        l.note = l.note.replace('<p>&nbsp;</p>', '')
        l.note = l.note.replace('<p></p>', '')


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

admin.site.register(Question)
