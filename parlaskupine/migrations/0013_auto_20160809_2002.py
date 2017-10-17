# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0012_auto_20160808_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpofpg',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
    ]