# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0006_taggedballots'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='gov_id',
            field=models.CharField(help_text='The ID of the official on the government website.', max_length=128, null=True, verbose_name='gov id'),
        ),
    ]
