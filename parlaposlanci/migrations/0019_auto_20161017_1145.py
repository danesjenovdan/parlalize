# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0018_auto_20161010_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpstaticpl',
            name='district',
            field=jsonfield.fields.JSONField(help_text='Voting district name.', null=True, blank=True),
        ),
    ]
