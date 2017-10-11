# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0020_organization_is_coalition'),
    ]

    operations = [
        migrations.AddField(
            model_name='workingbodies',
            name='viceMember',
            field=jsonfield.fields.JSONField(default=0),
            preserve_default=False,
        ),
    ]
