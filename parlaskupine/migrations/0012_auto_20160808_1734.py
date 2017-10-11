# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0011_auto_20160805_2244'),
    ]

    operations = [
        migrations.CreateModel(
            name='VocabularySize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('score', models.FloatField(help_text='Vacabularty size of this Org', null=True, verbose_name='Vacabularty size of this Org', blank=True)),
                ('average', models.FloatField(help_text='Vacabularty size of Org', null=True, verbose_name='average', blank=True)),
                ('maximum', models.FloatField(help_text='Max of Org vacabularty size ', null=True, verbose_name='max', blank=True)),
                ('maxOrg', models.ForeignKey(related_name='childrenVacSiz', blank=True, to='parlaskupine.Organization', help_text='Organization which has max vacabularty size', null=True)),
                ('organization', models.ForeignKey(related_name='childrenVS', blank=True, to='parlaskupine.Organization', help_text='Org', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
