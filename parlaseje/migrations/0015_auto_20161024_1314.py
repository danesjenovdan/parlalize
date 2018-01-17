# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0014_auto_20161007_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True),
        ),
    ]
