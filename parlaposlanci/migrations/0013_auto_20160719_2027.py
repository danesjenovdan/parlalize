# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0012_auto_20160714_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presence',
            name='average_sessions',
            field=models.FloatField(help_text='Average of MP attended sessions', null=True, verbose_name='average', blank=True),
        ),
        migrations.AlterField(
            model_name='presence',
            name='average_votes',
            field=models.FloatField(help_text='Average of MP attended sessions', null=True, verbose_name='average', blank=True),
        ),
        migrations.AlterField(
            model_name='presence',
            name='maximum_sessions',
            field=models.FloatField(help_text='Max of MP attended sessions', null=True, verbose_name='max', blank=True),
        ),
        migrations.AlterField(
            model_name='presence',
            name='maximum_votes',
            field=models.FloatField(help_text='Max of MP attended sessions', null=True, verbose_name='max', blank=True),
        ),
        migrations.AlterField(
            model_name='presence',
            name='person_value_sessions',
            field=models.FloatField(help_text='Presence of this MP', null=True, verbose_name='Presence of this MP', blank=True),
        ),
        migrations.AlterField(
            model_name='presence',
            name='person_value_votes',
            field=models.FloatField(help_text='Presence of this MP', null=True, verbose_name='Presence of this MP', blank=True),
        ),
    ]
