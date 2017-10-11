# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0026_presencethroughtime'),
        ('parlaseje', '0020_auto_20170109_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='organizations',
            field=models.ManyToManyField(help_text=b'The organizations in session', related_name='sessions', to='parlaskupine.Organization'),
        ),
        migrations.AddField(
            model_name='vote',
            name='document_url',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='organization',
            field=models.ForeignKey(related_name='session', blank=True, to='parlaskupine.Organization', help_text=b'The organization in session', null=True),
        ),
    ]
