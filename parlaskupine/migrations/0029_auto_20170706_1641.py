# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0028_auto_20170613_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
    ]
