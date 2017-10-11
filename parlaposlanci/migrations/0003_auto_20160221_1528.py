# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0002_auto_20151115_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='cutvotes',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='created_for',
            field=models.DateField(help_text='date of activity', null=True, verbose_name='date of actanalizeivity', blank=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='created_for',
            field=models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True),
        ),
    ]
