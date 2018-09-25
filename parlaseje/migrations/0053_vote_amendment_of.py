# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-19 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0031_auto_20180820_1140'),
        ('parlaseje', '0052_remove_vote_amendment_of'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='amendment_of',
            field=models.ManyToManyField(related_name='amendments', through='parlaseje.AmendmentOfOrg', to='parlaskupine.Organization'),
        ),
    ]
