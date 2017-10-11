# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0011_auto_20160714_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocabularysize',
            name='average',
            field=models.FloatField(help_text='Vacabularty size of MP', null=True, verbose_name='average', blank=True),
        ),
        migrations.AlterField(
            model_name='vocabularysize',
            name='maximum',
            field=models.FloatField(help_text='Max of MP vacabularty size ', null=True, verbose_name='max', blank=True),
        ),
        migrations.AlterField(
            model_name='vocabularysize',
            name='score',
            field=models.FloatField(help_text='Vacabularty size of this MP', null=True, verbose_name='Vacabularty size of this MP', blank=True),
        ),
    ]
