# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0013_auto_20160719_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpstaticpl',
            name='gender',
            field=models.CharField(default=b'f', help_text='Gender', max_length=1),
        ),
    ]
