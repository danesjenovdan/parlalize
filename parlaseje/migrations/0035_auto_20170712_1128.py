# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0034_vote_amendment_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='vote',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
    ]
