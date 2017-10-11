# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0015_auto_20160803_1826'),
        ('parlaskupine', '0015_auto_20160819_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkingBodies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('vice_president', jsonfield.fields.JSONField()),
                ('members', jsonfield.fields.JSONField()),
                ('coal_ratio', models.FloatField()),
                ('oppo_ratio', models.FloatField()),
                ('seats', jsonfield.fields.JSONField()),
                ('sessions', jsonfield.fields.JSONField()),
                ('organization', models.ForeignKey(to='parlaskupine.Organization')),
                ('president', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='President', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
