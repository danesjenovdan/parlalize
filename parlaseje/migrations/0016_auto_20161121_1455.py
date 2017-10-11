# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0015_auto_20161024_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='created_at',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False),
        ),
        migrations.AddField(
            model_name='quote',
            name='updated_at',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False),
        ),
    ]
