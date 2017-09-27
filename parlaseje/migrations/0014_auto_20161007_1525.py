# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0013_auto_20160913_1857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote_graph',
            name='id_parladata',
        ),
        migrations.AddField(
            model_name='vote_graph',
            name='vote',
            field=models.ForeignKey(related_name='vote_of_graph', blank=True, to='parlaseje.Vote', help_text='Vote', null=True),
        ),
    ]
