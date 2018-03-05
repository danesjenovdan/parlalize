# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0033_auto_20171011_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='mismatchofpg',
            name='average',
            field=models.FloatField(help_text='Average score', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='mismatchofpg',
            name='maxMP',
            field=models.ForeignKey(related_name='mismatches', blank=True, to='parlaposlanci.Person', help_text='Person who has max mismatch of PG', null=True),
        ),
        migrations.AddField(
            model_name='mismatchofpg',
            name='maximum',
            field=models.FloatField(help_text='Maximum score', null=True, blank=True),
        ),
    ]
