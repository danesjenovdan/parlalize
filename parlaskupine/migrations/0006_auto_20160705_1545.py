# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0005_auto_20160623_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='percentofattendedsession',
            name='average',
        ),
        migrations.RemoveField(
            model_name='percentofattendedsession',
            name='maxPG',
        ),
        migrations.RemoveField(
            model_name='percentofattendedsession',
            name='maximum',
        ),
        migrations.RemoveField(
            model_name='percentofattendedsession',
            name='organization_value',
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='average_sessions',
            field=models.FloatField(help_text='Average of PG attended sessions', null=True, verbose_name='average', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='average_votes',
            field=models.FloatField(help_text='Average of PG attended sessions', null=True, verbose_name='average', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='maxPG_sessions',
            field=jsonfield.fields.JSONField(help_text='PG who has max prfesence of sessions', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='maxPG_votes',
            field=jsonfield.fields.JSONField(help_text='PG who has max prfesence of sessions', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='maximum_sessions',
            field=models.FloatField(help_text='Max of PG attended sessions', null=True, verbose_name='max', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='maximum_votes',
            field=models.FloatField(help_text='Max of PG attended sessions', null=True, verbose_name='max', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='organization_value_sessions',
            field=models.FloatField(help_text='Presence of this PG', null=True, verbose_name='Presence of this PG', blank=True),
        ),
        migrations.AddField(
            model_name='percentofattendedsession',
            name='organization_value_votes',
            field=models.FloatField(help_text='Presence of this PG', null=True, verbose_name='Presence of this PG', blank=True),
        ),
    ]
