# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0028_auto_20170706_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', db_index=True, blank=True),
        ),
    ]
