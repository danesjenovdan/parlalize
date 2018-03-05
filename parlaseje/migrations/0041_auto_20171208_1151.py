# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0030_pgmismatch'),
        ('parlaseje', '0040_auto_20171011_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegislationNote',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('parlaseje.legislation',),
        ),
        migrations.RemoveField(
            model_name='legislation',
            name='session',
        ),
        migrations.AddField(
            model_name='legislation',
            name='abstractVisible',
            field=models.BooleanField(default=False, help_text=b'Is abstract visible'),
        ),
        migrations.AddField(
            model_name='legislation',
            name='classification',
            field=models.CharField(help_text=b'Classification of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='date',
            field=parlaseje.models.PopoloDateTimeField(help_text=b'Time of last procudure', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='icon',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='is_exposed',
            field=models.BooleanField(default=False, help_text=b'Is abstract visible'),
        ),
        migrations.AddField(
            model_name='legislation',
            name='mdt_fk',
            field=models.ForeignKey(related_name='laws', blank=True, to='parlaskupine.Organization', max_length=255, help_text=b'MDT object', null=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='procedure',
            field=models.CharField(help_text=b'Procedure of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='procedure_ended',
            field=models.BooleanField(default=False, help_text=b'Procedure phase of law'),
        ),
        migrations.AddField(
            model_name='legislation',
            name='procedure_phase',
            field=models.CharField(help_text=b'Procedure phase of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='proposer_text',
            field=models.CharField(help_text=b'Proposer of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='sessions',
            field=models.ManyToManyField(help_text=b'The legislative session in which the motion was proposed', related_name='laws', null=True, to='parlaseje.Session', blank=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='status',
            field=models.CharField(default=b'v obravnavi', choices=[(b'v obravnavi', b'v obravnavi'), (b'konec obravnave', b'konec obravnave')], max_length=255, blank=True, help_text=b'result of law', null=True),
        ),
        migrations.AddField(
            model_name='legislation',
            name='type_of_law',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='classification',
            field=models.CharField(help_text=b'classification', max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='legislation',
            name='result',
            field=models.CharField(blank=True, max_length=255, null=True, help_text=b'result of law', choices=[(None, b'Prazno'), (b'sprejet', b'sprejet'), (b'zavrnjen', b'zavrnjen')]),
        ),
        migrations.AlterField(
            model_name='vote',
            name='law',
            field=models.ForeignKey(related_name='votes', blank=True, to='parlaseje.Legislation', help_text='Legislation foreign key', null=True),
        ),
    ]
