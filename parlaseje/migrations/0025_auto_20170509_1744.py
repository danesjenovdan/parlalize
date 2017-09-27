# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0024_auto_20170415_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote_analysis',
            name='pgs_data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
