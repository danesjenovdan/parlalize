# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0034_auto_20171209_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpstaticpl',
            name='birth_date',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
    ]
