# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote_graph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('motion', models.TextField(help_text=b'The motion for which the vote took place', null=True, blank=True)),
                ('votes_for', models.IntegerField(help_text=b'Number of votes for', null=True, blank=True)),
                ('against', models.IntegerField(help_text=b'Number votes againt', null=True, blank=True)),
                ('abstain', models.IntegerField(help_text=b'Number votes abstain', null=True, blank=True)),
                ('not_present', models.IntegerField(help_text=b'Number of MPs that warent on the session', null=True, blank=True)),
                ('result', models.NullBooleanField(default=False, help_text=b'The result of the vote')),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('pgs_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
