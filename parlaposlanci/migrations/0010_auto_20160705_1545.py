# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0009_auto_20160623_1715'),
    ]

    operations = [
        migrations.RenameField(
            model_name='presence',
            old_name='average',
            new_name='average_sessions',
        ),
        migrations.RenameField(
            model_name='presence',
            old_name='maximum',
            new_name='maximum_sessions',
        ),
        migrations.RenameField(
            model_name='presence',
            old_name='person_value',
            new_name='person_value_sessions',
        ),
        migrations.RemoveField(
            model_name='presence',
            name='maxMP',
        ),
        migrations.AddField(
            model_name='presence',
            name='average_votes',
            field=models.IntegerField(help_text='Average of MP attended sessions', null=True, verbose_name='average', blank=True),
        ),
        migrations.AddField(
            model_name='presence',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='presence',
            name='maxMP_sessions',
            field=jsonfield.fields.JSONField(help_text='Person who has max presence of sessions', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='presence',
            name='maxMP_votes',
            field=jsonfield.fields.JSONField(help_text='Person who has max presence of sessions', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='presence',
            name='maximum_votes',
            field=models.IntegerField(help_text='Max of MP attended sessions', null=True, verbose_name='max', blank=True),
        ),
        migrations.AddField(
            model_name='presence',
            name='person_value_votes',
            field=models.IntegerField(help_text='Presence of this MP', null=True, verbose_name='Presence of this MP', blank=True),
        ),
    ]
