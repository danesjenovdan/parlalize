# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0019_auto_20170108_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='content_link',
            field=models.URLField(help_text=b'Words spoken', max_length=350, null=True, blank=True),
        ),
    ]
