# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0010_auto_20160705_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='averagenumberofspeechespersession',
            name='created_for',
            field=models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True),
        ),
        migrations.AddField(
            model_name='numberofspeechespersession',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='spokenwords',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='vocabularysize',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AlterField(
            model_name='numberofspeechespersession',
            name='average',
            field=models.FloatField(help_text='Average of MP speeches per session', null=True, verbose_name='average', blank=True),
        ),
        migrations.AlterField(
            model_name='numberofspeechespersession',
            name='maximum',
            field=models.FloatField(help_text='Max of MP speeches per session', null=True, verbose_name='max', blank=True),
        ),
        migrations.AlterField(
            model_name='numberofspeechespersession',
            name='person_value',
            field=models.FloatField(help_text='Number of speeches of this MP', null=True, verbose_name='Number of speeches of this MP', blank=True),
        ),
    ]
