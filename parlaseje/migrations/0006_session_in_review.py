# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0005_remove_vote_created_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='in_review',
            field=models.BooleanField(default=False, help_text=b'Is session in review?'),
        ),
    ]
