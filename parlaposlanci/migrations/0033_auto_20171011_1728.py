# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0032_auto_20171011_1712'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mpstaticpl',
            old_name='party_id',
            new_name='party',
        ),
    ]
