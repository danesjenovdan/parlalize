# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0027_auto_20170511_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='intra_disunion',
            field=models.FloatField(default=0.0, help_text=b'intra disunion for all members'),
        ),
    ]
