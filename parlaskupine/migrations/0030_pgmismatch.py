# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0029_auto_20170706_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='PGMismatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('created_for', models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True)),
                ('organization', models.ForeignKey(related_name='mismatches', blank=True, to='parlaskupine.Organization', help_text='PG', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
