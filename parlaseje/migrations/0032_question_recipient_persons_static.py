# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0027_ministerstatic'),
        ('parlaseje', '0031_auto_20170613_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='recipient_persons_static',
            field=models.ManyToManyField(help_text=b"Recipient persons (if it's a person).", related_name='questions_static', null=True, to='parlaposlanci.MinisterStatic', blank=True),
        ),
    ]
