# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import tinymce.models
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0039_auto_20170821_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='Legislation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('text', models.TextField(help_text=b'The text of the motion', null=True, blank=True)),
                ('epa', models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True)),
                ('mdt', models.CharField(help_text=b'Working body', max_length=255, null=True, blank=True)),
                ('result', models.CharField(help_text=b'result of law', max_length=255, null=True, blank=True)),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('note', tinymce.models.HTMLField(null=True, blank=True)),
                ('session', models.ForeignKey(blank=True, to='parlaseje.Session', help_text=b'The legislative session in which the motion was proposed', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='vote',
            name='epa',
            field=models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='law',
            field=models.ForeignKey(related_name='legislation', blank=True, to='parlaseje.Legislation', help_text='Legislation foreign key', null=True),
        ),
    ]
