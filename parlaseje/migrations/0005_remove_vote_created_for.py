# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0004_vote_created_for'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='created_for',
        ),
    ]
