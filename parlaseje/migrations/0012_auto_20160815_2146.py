# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0011_auto_20160805_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote_graph',
            name='created_for',
            field=models.DateField(help_text='date of vote', null=True, verbose_name='date of vote', blank=True),
        ),
        migrations.AddField(
            model_name='vote_graph',
            name='session',
            field=models.ForeignKey(related_name='in_session_for_VG', blank=True, to='parlaseje.Session', help_text='Session ', null=True),
        ),
    ]
