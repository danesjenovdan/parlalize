# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0043_auto_20180717_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='speech',
            name='agenda_item_order',
            field=models.IntegerField(help_text=b'Order of speech', null=True, blank=True),
        ),
    ]
