# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0019_auto_20161017_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='id_parladata',
            field=models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True),
        ),
    ]
