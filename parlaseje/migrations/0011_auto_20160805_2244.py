# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0010_averagespeeches'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(help_text='tag name', null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='tags',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
    ]
