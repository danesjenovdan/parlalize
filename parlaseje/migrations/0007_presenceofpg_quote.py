# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0006_session_in_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='PresenceOfPG',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('presence', jsonfield.fields.JSONField(null=True, blank=True)),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quoted_text', models.TextField(help_text='text quoted in a speech', null=True, verbose_name='quoted text', blank=True)),
                ('first_char', models.IntegerField(help_text='index of first character of quote string', null=True, blank=True)),
                ('last_char', models.IntegerField(help_text='index of last character of quote string', null=True, blank=True)),
                ('speech', models.ForeignKey(help_text='the speech that is being quoted', to='parlaseje.Speech')),
            ],
        ),
    ]
