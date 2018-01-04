# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0041_auto_20171208_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='legislation',
            name='extra_note',
            field=tinymce.models.HTMLField(null=True, blank=True),
        ),
    ]
