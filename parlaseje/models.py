# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from behaviors.models import Timestampable, Versionable
from parlalize.settings import (API_OUT_DATE_FORMAT, API_DATE_FORMAT,
                                LEGISLATION_STATUS, LEGISLATION_RESULT)
from datetime import datetime
from tinymce.models import HTMLField


class PopoloDateTimeField(models.DateTimeField):
    """Converting datetime to popolo."""

    def get_popolo_value(self, value):
        return str(datetime.strftime(value, '%Y-%m-%d'))


class Session(Timestampable, models.Model):
    """Model of all sessions that happened in parliament, copied from parladata."""

    name = models.CharField(_('name'),
                            blank=True, null=True,
                            max_length=512,
                            help_text=_('Session name'))

    date = PopoloDateTimeField(_('date of session'),
                               blank=True, null=True,
                               help_text=_('date of session'))

    id_parladata = models.IntegerField(_('parladata id'),
                                       db_index=True,
                                       blank=True, null=True,
                                       help_text=_('id parladata'))

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
                                     related_name='session',
                                     help_text='The organization in session')

    organizations = models.ManyToManyField('parlaskupine.Organization',
                                           related_name='sessions',
                                           help_text='The organizations in session')

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    actived = models.CharField(_('actived'),
                               null=True, blank=True,
                               max_length=128,
                               help_text=_('Yes if PG is actived or no if it is not'))

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      blank=True, null=True,
                                      help_text=_('An organization category, e.g. committee'))

    gov_id = models.TextField(blank=True, null=True,
                              help_text='Gov website ID.')

    in_review = models.BooleanField(default=False,
                                    help_text='Is session in review?')

    def __str__(self):
        return self.name

    def getSessionDataMultipleOrgs(self):
        orgs_data = [org.getOrganizationData()
                     for org
                     in self.organizations.all()]
        return {'name': self.name,
                'date': self.start_time.strftime(API_OUT_DATE_FORMAT),
                'date_ts': self.start_time,
                'id': self.id_parladata,
                'orgs': orgs_data,
                'in_review': self.in_review}

    def getSessionData(self):
        orgs_data = [org.getOrganizationData()
                     for org
                     in self.organizations.all()]
        activity = Activity.objects.filter(session=self)
        if activity:
            last_day = activity.latest('updated_at').updated_at.strftime(API_OUT_DATE_FORMAT)
        else:
            last_day = self.start_time.strftime(API_OUT_DATE_FORMAT),
        return {'name': self.name,
                'date': self.start_time.strftime(API_OUT_DATE_FORMAT),
                'updated_at': last_day,
                'date_ts': self.start_time,
                'id': self.id_parladata,
                'org': self.organization.getOrganizationData(),
                'orgs': orgs_data,
                'in_review': self.in_review}


class Activity(Timestampable, models.Model):
    """All activities of MP."""

    id_parladata = models.IntegerField(_('parladata id'),
                                       db_index=True,
                                       blank=True, null=True,
                                       help_text=_('id parladata'))

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name="%(app_label)s_%(class)s_related",
                                help_text=_('Session '))

    person = models.ManyToManyField('parlaposlanci.Person',
                                     blank=True,
                                     help_text=_('MP'))

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    def get_child(self):
        if Speech.objects.filter(activity_ptr=self.id):
            return Speech.objects.get(activity_ptr=self.id)
        elif Ballot.objects.filter(activity_ptr=self.id):
            return Ballot.objects.get(activity_ptr=self.id)
        else:
            return Question.objects.get(activity_ptr=self.id)


class Speech(Versionable, Activity):
    """Model of all speeches in parlament."""

    content = models.TextField(blank=True, null=True,
                               help_text='Words spoken')

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')

    agenda_item_order = models.IntegerField(blank=True, null=True,
                                            help_text='Order of speech')

    the_order = models.IntegerField(blank=True, null=True,
                                    help_text='Absolute order on session',
                                    db_index=True,)

    organization = models.ForeignKey('parlaskupine.Organization',
                                     blank=True, null=True,
                                     help_text='Organization')

    debate = models.ForeignKey('Debate',
                               blank=True, null=True,
                               related_name='speeches',
                               help_text=_('debate '))



    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)

    @staticmethod
    def getValidSpeeches(date_):
        return Speech.objects.filter(valid_from__lt=date_, valid_to__gt=date_)


class Question(Activity):
    """Model of MP questions to the government."""

    content_link = models.URLField(help_text='Words spoken',
                                   max_length=350,
                                   blank=True, null=True)

    title = models.TextField(blank=True, null=True,
                             help_text='Words spoken')

    author_org = models.ForeignKey('parlaskupine.Organization',
                                   blank=True, null=True,
                                   related_name='AuthorOrg',
                                   help_text=_('Author organization'))

    author_orgs = models.ManyToManyField('parlaskupine.Organization',
                                         blank=True,
                                         help_text=_('Author organizations'))

    recipient_persons = models.ManyToManyField('parlaposlanci.Person',
                                               blank=True,
                                               help_text='Recipient persons (if it\'s a person).',
                                               related_name='questions')
    recipient_persons_static = models.ManyToManyField('parlaposlanci.MinisterStatic',
                                                      blank=True,
                                                      help_text='Recipient persons (if it\'s a person).',
                                                      related_name='questions_static')
    recipient_organizations = models.ManyToManyField('parlaskupine.Organization',
                                                     blank=True,
                                                     help_text='Recipient organizations (if it\'s an organization).',
                                                     related_name='questions_org')
    recipient_text = models.TextField(blank=True,
                                      null=True,
                                      help_text='Recipient name as written on dz-rs.si')
    type_of_question = models.CharField(max_length=64,
                                        blank=True,
                                        null=True)
    answer_date = PopoloDateTimeField(blank=True, null=True,
                                      help_text='Answer date')

    def getQuestionData(self, ministerStatic = None):
        persons = []
        orgs = []
        if ministerStatic:
            persons = [ministerStatic[str(ministr.id)] for ministr in self.recipient_persons_static.all()]
        else:
            persons = [ministr.getJsonData() for ministr in self.recipient_persons_static.all()]
        for org in self.recipient_organizations.all():
            orgs.append(org.getOrganizationData())
        return {'title': self.title,
                'recipient_text': self.recipient_text,
                'content_url': self.content_link,
                'recipient_persons': persons,
                'recipient_orgs': orgs,
                'url': self.content_link,
                'id': self.id_parladata,
                'session_name': self.session.name if self.session else None,
                'session_id': self.session.id_parladata if self.session else None,
                'type_of_question': self.type_of_question,
                'answer_date': self.answer_date if self.answer_date else None,
                'question_date': self.start_time if self.start_time else None}


class Ballot(Activity):
    """Model of all ballots"""

    vote = models.ForeignKey('Vote',
                             blank=True, null=True,
                             related_name='vote',
                             help_text=_('Vote'))

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain')

    voter_party = models.ForeignKey('parlaskupine.Organization',
                                    blank=True, null=True,
                                    related_name='ballotsOfVoters',
                                    help_text=_('Party of voter'))

    org_voter = models.ForeignKey('parlaskupine.Organization',
                                  blank=True, null=True,
                                  related_name='OrganizationVoter',
                                  help_text=_('Organization voter'))

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)


class AmendmentOfOrg(Timestampable, models.Model):
    vote = models.ForeignKey('Vote')
    organization = models.ForeignKey('parlaskupine.Organization')


class Vote(Timestampable, models.Model):
    """Model of all votes that happend on specific sessions,
       with number of votes for, against, abstain and not present.
    """

    created_for = models.DateField(_('date of vote'),
                                   blank=True, null=True,
                                   help_text=_('date of vote'))

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name='in_session',
                                help_text=_('Session '))

    motion = models.TextField(blank=True, null=True,
                              help_text='The motion for which the vote took place')

    tags = JSONField(blank=True, null=True)

    votes_for = models.IntegerField(blank=True, null=True,
                                    help_text='Number of votes for')

    against = models.IntegerField(blank=True, null=True,
                                  help_text='Number votes againt')

    abstain = models.IntegerField(blank=True, null=True,
                                  help_text='Number votes abstain')

    not_present = models.IntegerField(blank=True, null=True,
                                      help_text='Number of MPs that warent on the session')

    result = models.NullBooleanField(blank=True, null=True,
                                     default=False,
                                     help_text='The result of the vote')

    id_parladata = models.IntegerField(_('parladata id'),
                                       db_index=True,
                                       blank=True, null=True,
                                       help_text=_('id parladata'))

    document_url = JSONField(blank=True,
                             null=True)

    start_time = PopoloDateTimeField(blank=True,
                                     null=True,
                                     help_text='Start time')

    is_outlier = models.NullBooleanField(default=False,
                                         help_text='is outlier')

    has_outlier_voters = models.NullBooleanField(default=False,
                                                 help_text='has outlier voters')

    intra_disunion = models.FloatField(default=0.0,
                                       help_text='intra disunion for all members')

    amendment_of = models.ManyToManyField('parlaskupine.Organization',
                                          related_name='amendments',
                                          through=AmendmentOfOrg)


    amendment_of_person = models.ManyToManyField('parlaposlanci.Person',
                                          related_name='amendments')

    abstractVisible = models.BooleanField(default=False,
                                          help_text='Is abstract visible')

    note = HTMLField(blank=True,
                     null=True)

    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    law = models.ForeignKey('Legislation',
                            blank=True, null=True,
                            related_name='votes',
                            help_text=_('Legislation foreign key'),
                            on_delete=models.SET_NULL)

    classification = models.CharField(blank=True, null=True,
                                      max_length=255,
                                      help_text='classification')

    agenda_item = models.ManyToManyField('AgendaItem', blank=True,
                                         help_text='Agenda item', related_name='votes')

    def __str__(self):
        return self.session.name + ' | ' + self.motion


class Vote_analysis(Timestampable, models.Model):

    session = models.ForeignKey('Session',
                               blank=True, null=True,
                               related_name='in_session_for_VA',
                               help_text=_('Session '))

    vote = models.ForeignKey('Vote',
                               blank=True, null=True,
                               related_name='analysis',
                               help_text=_('Vote'))

    created_for = models.DateField(_('date of vote'),
                                    blank=True,
                                    null=True,
                                    help_text=_('date of vote'))

    votes_for = models.IntegerField(blank=True, null=True,
                                   help_text='Number of votes for')

    against = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes againt')

    abstain = models.IntegerField(blank=True, null=True,
                                   help_text='Number votes abstain')

    not_present = models.IntegerField(blank=True, null=True,
                                   help_text='Number of MPs that warent on the session')
    pgs_data = JSONField(blank=True, null=True)

    mp_yes = JSONField(blank=True, null=True)
    mp_no = JSONField(blank=True, null=True)
    mp_np = JSONField(blank=True, null=True)
    mp_kvor = JSONField(blank=True, null=True)

    coal_opts = JSONField(blank=True, null=True)

    oppo_opts = JSONField(blank=True, null=True)


class AbsentMPs(Timestampable, models.Model):
    """Model for analysis absent MPs on session."""

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name='session_absent',
                                help_text=_('Session '))

    absentMPs = JSONField(blank=True, null=True)

    created_for = models.DateField(_('date of vote'),
                                   blank=True, null=True,
                                   help_text=_('date of vote'))


class Quote(Timestampable, models.Model):
    """Model for quoted text from speeches."""

    quoted_text = models.TextField(_('quoted text'),
                                   blank=True, null=True,
                                   help_text=_('text quoted in a speech'))

    speech = models.ForeignKey('Speech',
                               help_text=_('the speech that is being quoted'))

    first_char = models.IntegerField(blank=True, null=True,
                                     help_text=_('index of first character of quote string'))

    last_char = models.IntegerField(blank=True, null=True,
                                    help_text=_('index of last character of quote string'))


class PresenceOfPG(Timestampable, models.Model):
    """Model for analysis presence of PG on session."""

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name='session_presence',
                                help_text=_('Session '))

    presence = JSONField(blank=True, null=True)

    created_for = models.DateField(_('date of activity'),
                                   blank=True, null=True,
                                   help_text=_('date of analize'))


class Tfidf(Timestampable, models.Model):
    """Model for analysis TFIDF."""

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name='tfidf',
                                help_text=_('Session '))

    created_for = models.DateField(_('date of activity'),
                                   blank=True,
                                   null=True,
                                   help_text=_('date of analize'))

    is_visible = models.BooleanField(_('is visible'),
                                     default=True)

    data = JSONField(blank=True, null=True)

    def __str__(self):
        return unicode(self.session.name) + " --> " + unicode(self.session.organization.name)


class Tag(models.Model):
    """All tags of votes."""

    id_parladata = models.IntegerField(_('parladata id'),
                                       blank=True,
                                       null=True,
                                       help_text=_('id parladata'))

    name = models.TextField(blank=True,
                            null=True,
                            help_text=_('tag name'))


class Legislation(Timestampable, models.Model):
    sessions = models.ManyToManyField('Session',
                                      blank=True,
                                      help_text='The legislative session in which the motion was proposed',
                                      related_name='laws')

    text = models.TextField(blank=True, null=True,
                            help_text='The text of the motion')

    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    mdt = models.CharField(blank=True, null=True,
                           max_length=1024,
                           help_text='Working body')

    mdt_fk = models.ForeignKey('parlaskupine.Organization',
                               related_name='laws',
                               blank=True, null=True,
                               max_length=255,
                               help_text='MDT object')

    status = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='result of law',
                              default=LEGISLATION_STATUS[0][0],
                              choices=LEGISLATION_STATUS)

    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='result of law',
                              choices=LEGISLATION_RESULT)

    id_parladata = models.IntegerField(_('parladata id'),
                                       blank=True,
                                       null=True,
                                       help_text=_('id parladata'))

    proposer_text = models.TextField(blank=True, null=True,
                                     help_text='Proposer of law')

    procedure_phase = models.CharField(blank=True, null=True,
                                       max_length=255,
                                       help_text='Procedure phase of law')

    procedure = models.CharField(blank=True, null=True,
                                 max_length=255,
                                 help_text='Procedure of law')

    type_of_law = models.CharField(blank=True, null=True,
                                   max_length=255)

    note = HTMLField(blank=True,
                     null=True)

    extra_note = HTMLField(blank=True,
                           null=True)

    abstractVisible = models.BooleanField(default=False,
                                          help_text='Is abstract visible')

    date = PopoloDateTimeField(blank=True,
                               null=True,
                               help_text='Time of last procudure')

    is_exposed = models.BooleanField(default=False,
                                     help_text='Is abstract visible')

    icon = models.CharField(blank=True, null=True,
                            max_length=255)

    procedure_ended = models.BooleanField(default=False,
                                          help_text='Procedure phase of law')

    classification = models.CharField(blank=True, null=True,
                                      max_length=255,
                                      help_text='Classification of law')
    has_discussion = models.BooleanField(default=False,
                                         help_text='Legislation has discusion')

    def __str__(self):
        #sessions = self.sessions.all().values_list('name', flat=True)
        sessions = []
        return ', '.join(sessions if sessions else '') + ' | ' + self.text if self.text else self.epa


class AgendaItem(Timestampable, models.Model):
    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                related_name='agenda_items',
                                help_text=_('Session '))

    title = models.CharField(blank=True, null=True,
                             max_length=1024,
                             help_text='Title of AgnedaItem')

    id_parladata = models.IntegerField(_('parladata id'),
                                       blank=True,
                                       null=True,
                                       help_text=_('id parladata'))

class Debate(Timestampable, models.Model):
    agenda_item = models.ManyToManyField('AgendaItem',
                                         blank=True,
                                         related_name='debates',
                                         help_text=_('AgendaItem '))

    date = models.DateField(_('date of debate'),
                            blank=True, null=True,
                            help_text=_('date of debate'))

    id_parladata = models.IntegerField(_('parladata id'),
                                       blank=True,
                                       null=True,
                                       help_text=_('id parladata'))
