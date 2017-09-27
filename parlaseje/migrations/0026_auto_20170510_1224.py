# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0025_auto_20170509_1744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote_analysis',
            name='pgs_kvor',
        ),
        migrations.RemoveField(
            model_name='vote_analysis',
            name='pgs_no',
        ),
        migrations.RemoveField(
            model_name='vote_analysis',
            name='pgs_np',
        ),
        migrations.RemoveField(
            model_name='vote_analysis',
            name='pgs_yes',
        ),
    ]
