# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0013_auto_20160809_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='mpofpg',
            name='organization',
            field=models.ForeignKey(related_name='MPOfPg_', blank=True, to='parlaskupine.Organization', help_text='PG', null=True),
        ),
    ]
