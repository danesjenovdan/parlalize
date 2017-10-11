# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0017_auto_20160823_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgstatic',
            name='viceOfPG',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
