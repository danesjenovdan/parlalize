# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0037_auto_20170810_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='abstractVisible',
            field=models.NullBooleanField(default=False, help_text=b'has outlier voters'),
        ),
    ]
