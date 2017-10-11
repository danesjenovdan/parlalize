# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0023_auto_20161203_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfidf',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='is visible'),
        ),
    ]
