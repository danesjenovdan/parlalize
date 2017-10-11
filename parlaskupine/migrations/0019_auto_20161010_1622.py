# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0018_auto_20160902_2301'),
    ]

    operations = [
        migrations.CreateModel(
            name='StyleScores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('problematicno', models.FloatField(help_text='Problematicno score of this PG', null=True, verbose_name='Problematicno style score of this PG', blank=True)),
                ('privzdignjeno', models.FloatField(help_text='Privzdignjeno style score of this PG', null=True, verbose_name='Privzdignjeno style score of this PG', blank=True)),
                ('preprosto', models.FloatField(help_text='Preprosto style score of this PG', null=True, verbose_name='Preprosto style score of this PG', blank=True)),
                ('problematicno_average', models.FloatField(help_text='Problematicno average style score', null=True, verbose_name='Problematicno average style score', blank=True)),
                ('privzdignjeno_average', models.FloatField(help_text='Privzdignjeno average style score', null=True, verbose_name='Privzdignjeno average style score', blank=True)),
                ('preprosto_average', models.FloatField(help_text='Preprosto average style score', null=True, verbose_name='Preprosto average style score', blank=True)),
                ('organization', models.ForeignKey(related_name='styleScores', blank=True, to='parlaskupine.Organization', help_text='Org', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='vocabularysize',
            name='organization',
            field=models.ForeignKey(related_name='vocabularySizes', blank=True, to='parlaskupine.Organization', help_text='Org', null=True),
        ),
    ]
