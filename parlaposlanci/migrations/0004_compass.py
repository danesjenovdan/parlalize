# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0003_auto_20160221_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('calculated_from', models.DateField(help_text='date of first ballot entered', null=True, verbose_name='date of first ballot entered', blank=True)),
                ('created_for', models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('person', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
