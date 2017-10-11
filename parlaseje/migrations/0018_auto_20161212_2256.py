# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0017_tfidf'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfidf',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='is visible'),
        ),
        migrations.AlterField(
            model_name='session',
            name='actived',
            field=models.CharField(help_text='Yes if PG is actived or no if it is not', max_length=128, null=True, verbose_name='actived', blank=True),
        ),
    ]
