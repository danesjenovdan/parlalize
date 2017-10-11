# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0020_district_id_parladata'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='has_function',
            field=models.BooleanField(default=False, help_text='True if is president or something special.'),
        ),
    ]
