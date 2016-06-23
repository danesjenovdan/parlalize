# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from parlaposlanci.models import *
from parlaseje.models import *

from behaviors.models import Timestampable

# converting datetime to popolo
class PopoloDateTimeField(models.DateTimeField):

    def get_popolo_value(self, value):
        return str(datetime.strftime(value, '%Y-%m-%d'))

# Create your models here.
@python_2_unicode_compatible
class Organization(Timestampable, models.Model):
    """
    A group with a common purpose or reason for existence that goes beyond the set of people belonging to it
    """

    name = models.TextField(_('name'),
                            help_text=_('A primary name, e.g. a legally recognized name'))

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))

    classification = models.TextField(_('Classification'), blank=True, null=True, help_text=_('Organization calssification.'))


    def __str__(self):
        return self.name

class PGStatic(Timestampable, models.Model):
    organization = models.ForeignKey('Organization', 
                                     help_text=_('Organization foreign key relationship'))

    created_for = models.DateField(_('date of activity'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of analize'))

    headOfPG = models.ForeignKey('parlaposlanci.Person', 
                                 related_name='PGStaticH', help_text=_('Head of MP'))

    viceOfPG = models.ForeignKey('parlaposlanci.Person' , 
                                 related_name='PGStaticV', help_text=_('Vice of MP'))

    numberOfSeats = models.IntegerField(blank = True, 
                                        null = True, 
                                        help_text = _('Number of seats in parlament of PG'))

    allVoters = models.IntegerField(blank=True, 
                                    null=True, 
                                    help_text=_('Number of voters'))

    facebook = models.TextField(blank=True, 
                                null=True, 
                                default=None, 
                                help_text=_('Facebook profile URL'))

    twitter = models.TextField(blank=True, 
                               null=True, 
                               default=None, 
                               help_text=_('Twitter profile URL'))

    email = models.TextField(blank=True, 
                             null=True, 
                             default=None, 
                             help_text=_('email profile URL'))

class PercentOFAttendedSession(Timestampable, models.Model): #Model for presence of PG on sessions

    organization = models.ForeignKey('Organization',
                               blank=True, null=True,
                               related_name='childrenPG',
                               help_text=_('PG'))

    organization_value = models.IntegerField(_('Presence of this PG'),
                                   blank=True, null=True,
                                   help_text=_('Presence of this PG'))


    maxPG = models.ForeignKey('Organization',
                               blank=True, null=True,
                               related_name='childrenMaxMP',
                               help_text=_('PG who has max prfesence of sessions'))


    average = models.IntegerField(_('average'),
                                   blank=True, null=True,
                                   help_text=_('Average of PG attended sessions'))

    maximum = models.IntegerField(_('max'),
                                   blank=True, null=True,
                                   help_text=_('Max of PG attended sessions'))


class MPOfPg(Timestampable, models.Model):

    id_parladata = models.IntegerField(_('parladata id'),
                            blank=True, null=True,help_text=_('id parladata'))

    MPs = JSONField(blank=True, null=True)


class MostMatchingThem(Timestampable, models.Model):

    organization = models.ForeignKey('Organization',
                           blank=True, null=True,
                           related_name='childrenMMT',
                           help_text=_('PG'))

    created_for = models.DateField(_('date of analize'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of analize'))

    person1 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenMMT1',
                                help_text=_('MP1'))

    votes1 = models.FloatField(_('MatchingThem1'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person2 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenMMT2',
                                help_text=_('MP2'))

    votes2 = models.FloatField(_('MatchingThem2'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person3 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenMMT3',
                                help_text=_('MP3'))

    votes3 = models.FloatField(_('MatchingThem3'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person4 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenMMT4',
                                help_text=_('MP4'))

    votes4 = models.FloatField(_('MatchingThem4'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person5 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenMMT5',
                                help_text=_('MP5'))

    votes5 = models.FloatField(_('MatchingThem5'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))


class LessMatchingThem(Timestampable, models.Model):

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='childrenLMT',
                                     help_text=_('PG'))

    created_for = models.DateField(_('date of analize'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of activity'))

    person1 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenLMT1',
                                help_text=_('MP1'))

    votes1 = models.FloatField(_('MatchingThem1'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person2 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenLMT2',
                                help_text=_('MP2'))

    votes2 = models.FloatField(_('MatchingThem2'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person3 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenLMT3',
                                help_text=_('MP3'))

    votes3 = models.FloatField(_('MatchingThem3'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person4 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenLMT4',
                                help_text=_('MP4'))

    votes4 = models.FloatField(_('MatchingThem4'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person5 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenLMT5',
                                help_text=_('MP5'))

    votes5 = models.FloatField(_('MatchingThem5'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))


class DeviationInOrganization(Timestampable, models.Model):

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='childrenD',
                                     help_text=_('PG'))

    created_for = models.DateField(_('date of analize'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of activity'))

    person1 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD1',
                                help_text=_('D1'))

    votes1 = models.FloatField(_('daviation1'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person2 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD2',
                                help_text=_('D2'))

    votes2 = models.FloatField(_('daviation2'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person3 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD3',
                                help_text=_('D3'))

    votes3 = models.FloatField(_('daviation3'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))

    person4 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD4',
                                help_text=_('D4'))

    votes4 = models.FloatField(_('daviation4'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))


    person5 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD5',
                                help_text=_('D5'))

    votes5 = models.FloatField(_('daviation5'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))


    person6 = models.ForeignKey('parlaposlanci.Person',
                                blank=True, null=True,
                                related_name='childrenD6',
                                help_text=_('D6'))

    votes6 = models.FloatField(_('daviation6'),
                               blank=True, null=True,
                               help_text=_('MatchingThem'))




class CutVotes(Timestampable, models.Model):
    created_for = models.DateField(_('date of activity'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of analize'))
    organization = models.ForeignKey("Organization")
    this_for = models.IntegerField()
    this_against = models.IntegerField()
    this_abstain = models.IntegerField()
    this_absent = models.IntegerField()
    coalition_for = models.IntegerField()
    coalition_against = models.IntegerField()
    coalition_abstain = models.IntegerField()
    coalition_absent = models.IntegerField()
    coalition_for_max = models.IntegerField()
    coalition_against_max = models.IntegerField()
    coalition_abstain_max = models.IntegerField()
    coalition_absent_max = models.IntegerField()
    coalition_for_max_org = models.CharField(max_length=500)
    coalition_against_max_org = models.CharField(max_length=500)
    coalition_abstain_max_org = models.CharField(max_length=500)
    coalition_absent_max_org = models.CharField(max_length=500)
    opposition_for = models.IntegerField()
    opposition_against = models.IntegerField()
    opposition_abstain = models.IntegerField()
    opposition_absent = models.IntegerField()
    opposition_for_max =models.IntegerField()
    opposition_against_max = models.IntegerField()
    opposition_abstain_max = models.IntegerField()
    opposition_absent_max = models.IntegerField()
    opposition_for_max_org = models.CharField(max_length=500)
    opposition_against_max_org = models.CharField(max_length=500)
    opposition_abstain_max_org = models.CharField(max_length=500)
    opposition_absent_max_org = models.CharField(max_length=500)