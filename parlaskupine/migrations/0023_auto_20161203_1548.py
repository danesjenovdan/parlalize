# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0022_tfidf'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person1',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person2',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person3',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person4',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person5',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='person6',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes1',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes2',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes3',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes4',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes5',
        ),
        migrations.RemoveField(
            model_name='deviationinorganization',
            name='votes6',
        ),
        migrations.AddField(
            model_name='deviationinorganization',
            name='data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
