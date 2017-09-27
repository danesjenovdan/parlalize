# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0016_auto_20161121_1455'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tfidf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('session', models.ForeignKey(related_name='tfidf', blank=True, to='parlaseje.Session', help_text='Session ', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
