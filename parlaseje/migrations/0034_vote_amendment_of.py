# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0029_auto_20170706_1641'),
        ('parlaseje', '0033_auto_20170627_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='amendment_of',
            field=models.ManyToManyField(related_name='amendments', to='parlaskupine.Organization'),
        ),
    ]
