# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0012_auto_20160815_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='absentmps',
            name='id_parladata',
        ),
        migrations.RemoveField(
            model_name='presenceofpg',
            name='id_parladata',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='id_parladata_session',
        ),
        migrations.AddField(
            model_name='absentmps',
            name='session',
            field=models.ForeignKey(related_name='session_absent', blank=True, to='parlaseje.Session', help_text='Session ', null=True),
        ),
        migrations.AddField(
            model_name='presenceofpg',
            name='session',
            field=models.ForeignKey(related_name='session_presence', blank=True, to='parlaseje.Session', help_text='Session ', null=True),
        ),
    ]
