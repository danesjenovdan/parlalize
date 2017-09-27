# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0019_auto_20161010_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='is_coalition',
            field=models.BooleanField(default=False, verbose_name='coalition'),
        ),
    ]
