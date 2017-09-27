# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0004_compass'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compass',
            name='person',
        ),
    ]
