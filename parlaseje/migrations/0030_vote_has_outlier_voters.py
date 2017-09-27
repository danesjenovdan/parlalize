# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0029_vote_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='has_outlier_voters',
            field=models.NullBooleanField(default=False, help_text=b'has outlier voters'),
        ),
    ]
