# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0024_mpstaticpl_working_bodies_functions'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberOfQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('score', models.FloatField(help_text='MP score', null=True, blank=True)),
                ('average', models.FloatField(help_text='Average score', null=True, blank=True)),
                ('maximum', models.FloatField(help_text='Maximum score', null=True, blank=True)),
                ('maxMPs', jsonfield.fields.JSONField(null=True, blank=True)),
                ('person', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
