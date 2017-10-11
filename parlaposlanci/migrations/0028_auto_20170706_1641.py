# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0027_ministerstatic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
    ]
