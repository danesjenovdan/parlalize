# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0027_auto_20170511_1806'),
        ('parlaskupine', '0026_presencethroughtime'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntraDisunion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('maximum', models.CharField(help_text='Maximum of organization disunion.', max_length=128, null=True, verbose_name='Maximum', blank=True)),
                ('organization', models.ForeignKey(related_name='intraDisunion', blank=True, to='parlaskupine.Organization', help_text='Org', null=True)),
                ('vote', models.ForeignKey(related_name='VoteintraDisunion', blank=True, to='parlaseje.Vote', help_text='Vote', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
