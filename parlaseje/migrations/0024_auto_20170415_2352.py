# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import parlaseje.models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0023_auto_20170331_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote_analysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of vote', null=True, verbose_name='date of vote', blank=True)),
                ('votes_for', models.IntegerField(help_text=b'Number of votes for', null=True, blank=True)),
                ('against', models.IntegerField(help_text=b'Number votes againt', null=True, blank=True)),
                ('abstain', models.IntegerField(help_text=b'Number votes abstain', null=True, blank=True)),
                ('not_present', models.IntegerField(help_text=b'Number of MPs that warent on the session', null=True, blank=True)),
                ('pgs_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
                ('coal_opts', jsonfield.fields.JSONField(null=True, blank=True)),
                ('oppo_opts', jsonfield.fields.JSONField(null=True, blank=True)),
                ('session', models.ForeignKey(related_name='in_session_for_VA', blank=True, to='parlaseje.Session', help_text='Session ', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='vote',
            name='is_outlier',
            field=models.NullBooleanField(default=False, help_text=b'is outlier'),
        ),
        #migrations.AddField(
        #    model_name='vote',
        #    name='start_time',
        #    field=parlaseje.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True),
        #),
        migrations.AddField(
            model_name='vote_analysis',
            name='vote',
            field=models.ForeignKey(related_name='analysis', blank=True, to='parlaseje.Vote', help_text='Vote', null=True),
        ),
    ]
