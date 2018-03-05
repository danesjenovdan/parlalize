# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import parlaseje.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0001_initial'),
        ('parlaposlanci', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('start_time', parlaseje.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parlaseje.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text='Session name', max_length=128, null=True, verbose_name='name', blank=True)),
                ('date', parlaseje.models.PopoloDateTimeField(help_text='date of session', null=True, verbose_name='date of session', blank=True)),
                ('mandate', models.CharField(help_text='Mandate name', max_length=128, null=True, verbose_name='mandate name', blank=True)),
                ('start_time', parlaseje.models.PopoloDateTimeField(help_text=b'Start time', null=True, verbose_name='start time of session', blank=True)),
                ('end_time', parlaseje.models.PopoloDateTimeField(help_text=b'End time', null=True, verbose_name='end time of session', blank=True)),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('actived', models.CharField(help_text='Yes if PG is actived or no if it is not', max_length=128, null=True, verbose_name='actived')),
                ('classification', models.CharField(help_text='An organization category, e.g. committee', max_length=128, null=True, verbose_name='classification', blank=True)),
                ('gov_id', models.TextField(help_text=b'Gov website ID.', null=True, blank=True)),
                ('organization', models.ForeignKey(related_name='organization', blank=True, to='parlaskupine.Organization', help_text=b'The organization in session', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('motion', models.TextField(help_text=b'The motion for which the vote took place', null=True, blank=True)),
                ('votes_for', models.IntegerField(help_text=b'Number of votes for', null=True, blank=True)),
                ('against', models.IntegerField(help_text=b'Number votes againt', null=True, blank=True)),
                ('abstain', models.IntegerField(help_text=b'Number votes abstain', null=True, blank=True)),
                ('not_present', models.IntegerField(help_text=b'Number of MPs that warent on the session', null=True, blank=True)),
                ('result', models.NullBooleanField(default=False, help_text=b'The result of the vote')),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('session', models.ForeignKey(related_name='in_session', blank=True, to='parlaseje.Session', help_text='Session ', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('activity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('option', models.CharField(help_text=b'Yes, no, abstain', max_length=128, null=True, blank=True)),
                ('vote', models.ForeignKey(related_name='vote', blank=True, to='parlaseje.Vote', help_text='Vote', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity',),
        ),
        migrations.CreateModel(
            name='Speech',
            fields=[
                ('activity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('content', models.TextField(help_text=b'Words spoken')),
                ('order', models.IntegerField(help_text=b'Order of speech', null=True, blank=True)),
                ('organization', models.ForeignKey(blank=True, to='parlaskupine.Organization', help_text='Organization', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity',),
        ),
        migrations.AddField(
            model_name='activity',
            name='person',
            field=models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='session',
            field=models.ForeignKey(related_name='parlaseje_activity_related', blank=True, to='parlaseje.Session', help_text='Session ', null=True),
        ),
    ]
