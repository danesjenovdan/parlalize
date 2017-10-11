# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0014_auto_20160811_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workingbodies',
            name='organization',
        ),
        migrations.DeleteModel(
            name='WorkingBodies',
        ),
    ]
