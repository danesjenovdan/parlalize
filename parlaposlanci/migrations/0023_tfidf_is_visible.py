# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0022_tfidf_created_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfidf',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='is visible'),
        ),
    ]
