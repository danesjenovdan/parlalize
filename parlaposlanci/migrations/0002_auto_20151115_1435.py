# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cutvotes',
            name='coalition_absent',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='coalition_absent_max',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='coalition_absent_max_person',
            field=models.CharField(default=0, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='opposition_absent',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='opposition_absent_max',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='opposition_absent_max_person',
            field=models.CharField(default=0, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='this_absent',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
