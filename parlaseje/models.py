# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
#from parlaposlanci.models import *
from jsonfield import JSONField
from behaviors.models import Timestampable

# converting datetime to popolo
class PopoloDateTimeField(models.DateTimeField):

    def get_popolo_value(self, value):
        return str(datetime.strftime(value, '%Y-%m-%d'))

# Create your models here.

#@python_2_unicode_compatible
class Session(Timestampable, models.Model): # poslanec, minister, predsednik dz etc.

    name = models.CharField(_('name'),
                            blank=True, null=True,
                            max_length=128,
                            help_text=_('Session name'))

    date = PopoloDateTimeField(_('date of session'),
                                     blank=True,
                                     null=True,
                                     help_text=_('date of session'))

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))

    mandate = models.CharField(_('mandate name'),
                            blank=True, null=True,
                            max_length=128,
                            help_text=_('Mandate name'))

    start_time = PopoloDateTimeField(_('start time of session'),
                                     blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(_('end time of session'),
                                   blank=True, null=True,
                                   help_text='End time')

    organization = models.ForeignKey('parlaskupine.Organization',
                                     blank=True, null=True,
                                     related_name='organization',
                                     help_text='The organization in session')

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))


    actived = models.CharField(_('actived'),
                            null=True,
                            max_length=128,
                            help_text=_('Yes if PG is actived or no if it is not'))

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      blank=True, null=True,
                                      help_text=_('An organization category, e.g. committee'))

    gov_id = models.TextField(blank=True, null=True, help_text='Gov website ID.')


    def __str__(self):
        return self.name

class Activity(Timestampable, models.Model):
    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))

    session = models.ForeignKey('Session',
                               blank=True, null=True,
                               related_name="%(app_label)s_%(class)s_related",
                               help_text=_('Session '))

    person = models.ForeignKey('parlaposlanci.Person',
                               blank=True, null=True,
                               help_text=_('MP'))


    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    def get_child(self):
        if Speech.objects.filter(activity_ptr=self.id):
            return Speech.objects.get(activity_ptr=self.id)
        else:
            return Ballot.objects.get(activity_ptr=self.id)

class Speech(Activity):
    content = models.TextField(help_text='Words spoken')
    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')
    organization = models.ForeignKey('parlaskupine.Organization', blank=True, null=True, help_text=_('Organization'))
    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)



class Ballot(Activity):
    vote = models.ForeignKey('Vote',
                               blank=True, null=True,
                               related_name='vote',
                               help_text=_('Vote'))

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain')

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)

class Vote(Timestampable, models.Model):
    session = models.ForeignKey('Session',
                               blank=True, null=True,
                               related_name='in_session',
                               help_text=_('Session '))

    motion = models.TextField(blank=True, null=True,
                              help_text='The motion for which the vote took place')

    votes_for = models.IntegerField(blank=True, null=True,
                                   help_text='Number of votes for')

    against = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes againt')

    abstain = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes abstain')

    not_present = models.IntegerField(blank=True, null=True,
                                   help_text='Number of MPs that warent on the session')

    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='The result of the vote')

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))


class Vote_graph(Timestampable, models.Model):

    motion = models.TextField(blank=True, null=True,
                              help_text='The motion for which the vote took place')


    votes_for = models.IntegerField(blank=True, null=True,
                                   help_text='Number of votes for')

    against = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes againt')

    abstain = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes abstain')

    not_present = models.IntegerField(blank=True, null=True,
                                   help_text='Number of MPs that warent on the session')

    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='The result of the vote')

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))

    pgs_yes = JSONField(blank=True, null=True)
    pgs_no = JSONField(blank=True, null=True)
    pgs_np = JSONField(blank=True, null=True)
    pgs_kvor = JSONField(blank=True, null=True)

    mp_yes = JSONField(blank=True, null=True)
    mp_no = JSONField(blank=True, null=True)
    mp_np = JSONField(blank=True, null=True)
    mp_kvor = JSONField(blank=True, null=True)
           
