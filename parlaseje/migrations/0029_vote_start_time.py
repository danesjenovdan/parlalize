# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0028_auto_20170512_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='start_time',
            field=parlaseje.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True),
        ),
    ]
