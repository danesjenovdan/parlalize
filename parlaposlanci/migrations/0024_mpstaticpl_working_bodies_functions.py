# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0023_tfidf_is_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpstaticpl',
            name='working_bodies_functions',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
