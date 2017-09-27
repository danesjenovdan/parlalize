# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0038_vote_abstractvisible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='abstractVisible',
            field=models.BooleanField(default=False, help_text=b'Is abstract visible'),
        ),
    ]
