# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0009_auto_20160623_1715'),
        ('parlaskupine', '0004_mpofpg'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviationinorganization',
            name='person3',
            field=models.ForeignKey(related_name='childrenD3', blank=True, to='parlaposlanci.Person', help_text='D3', null=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='person4',
            field=models.ForeignKey(related_name='childrenD4', blank=True, to='parlaposlanci.Person', help_text='D4', null=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='person5',
            field=models.ForeignKey(related_name='childrenD5', blank=True, to='parlaposlanci.Person', help_text='D5', null=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='person6',
            field=models.ForeignKey(related_name='childrenD6', blank=True, to='parlaposlanci.Person', help_text='D6', null=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='votes3',
            field=models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation3', blank=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='votes4',
            field=models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation4', blank=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='votes5',
            field=models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation5', blank=True),
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='votes6',
            field=models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation6', blank=True),
        ),
        migrations.AddField(
            model_name='pgstatic',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
    ]
