# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0002_deviationinorganization_lessmatchingthem_mostmatchingthem'),
    ]

    operations = [
        migrations.CreateModel(
            name='CutVotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('this_for', models.IntegerField()),
                ('this_against', models.IntegerField()),
                ('this_abstain', models.IntegerField()),
                ('this_absent', models.IntegerField()),
                ('coalition_for', models.IntegerField()),
                ('coalition_against', models.IntegerField()),
                ('coalition_abstain', models.IntegerField()),
                ('coalition_absent', models.IntegerField()),
                ('coalition_for_max', models.IntegerField()),
                ('coalition_against_max', models.IntegerField()),
                ('coalition_abstain_max', models.IntegerField()),
                ('coalition_absent_max', models.IntegerField()),
                ('coalition_for_max_org', models.CharField(max_length=500)),
                ('coalition_against_max_org', models.CharField(max_length=500)),
                ('coalition_abstain_max_org', models.CharField(max_length=500)),
                ('coalition_absent_max_org', models.CharField(max_length=500)),
                ('opposition_for', models.IntegerField()),
                ('opposition_against', models.IntegerField()),
                ('opposition_abstain', models.IntegerField()),
                ('opposition_absent', models.IntegerField()),
                ('opposition_for_max', models.IntegerField()),
                ('opposition_against_max', models.IntegerField()),
                ('opposition_abstain_max', models.IntegerField()),
                ('opposition_absent_max', models.IntegerField()),
                ('opposition_for_max_org', models.CharField(max_length=500)),
                ('opposition_against_max_org', models.CharField(max_length=500)),
                ('opposition_abstain_max_org', models.CharField(max_length=500)),
                ('opposition_absent_max_org', models.CharField(max_length=500)),
                ('organization', models.ForeignKey(to='parlaskupine.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
