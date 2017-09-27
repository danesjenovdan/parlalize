# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0008_auto_20160628_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='absentmps',
            name='created_for',
            field=models.DateField(help_text='date of vote', null=True, verbose_name='date of vote', blank=True),
        ),
    ]
