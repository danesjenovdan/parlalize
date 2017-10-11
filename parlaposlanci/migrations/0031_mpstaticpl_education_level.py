# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0030_auto_20170809_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpstaticpl',
            name='education_level',
            field=models.TextField(help_text="Person's education level", null=True, blank=True),
        ),
    ]
