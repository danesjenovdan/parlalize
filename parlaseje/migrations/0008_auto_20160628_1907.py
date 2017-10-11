# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0007_presenceofpg_quote'),
    ]

    operations = [
        migrations.AddField(
            model_name='presenceofpg',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='created_for',
            field=models.DateField(help_text='date of vote', null=True, verbose_name='date of vote', blank=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='id_parladata_session',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
