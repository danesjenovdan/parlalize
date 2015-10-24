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
    organization = models.ForeignKey('Organization', help_text=_('Organization foreign key relationship'))

    headOfPG = models.ForeignKey('parlaposlanci.Person' , related_name='PGStaticH', help_text=_('Head of MP'))

    viceOfPG = models.ForeignKey('parlaposlanci.Person' , related_name='PGStaticV', help_text=_('Vice of MP'))

    numberOfSeats = models.IntegerField(blank = True, null = True, help_text = _('Number of seats in parlament of PG'))

    allVoters = models.IntegerField(blank=True, null=True, help_text=_('Number of voters'))

    facebook = models.TextField(blank=True, null=True, default=None, help_text=_('Facebook profile URL'))
    twitter = models.TextField(blank=True, null=True, default=None, help_text=_('Twitter profile URL'))
    email = models.TextField(blank=True, null=True, default=None, help_text=_('email profile URL'))

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