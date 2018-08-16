# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0042_legislation_extra_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legislation',
            name='sessions',
            field=models.ManyToManyField(help_text=b'The legislative session in which the motion was proposed', related_name='laws', to='parlaseje.Session', blank=True),
        ),
    ]
