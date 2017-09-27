# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0006_auto_20160705_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='acronym',
            field=models.CharField(help_text='Organization acronym', max_length=128, null=True, verbose_name='acronym', blank=True),
        ),
    ]
