# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0017_stylescores_created_for'),
    ]

    operations = [
        migrations.CreateModel(
            name='VocabularySizeUniqueWords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('score', models.FloatField(help_text='Vacabularty size of this MP', null=True, verbose_name='Vacabularty size of this MP', blank=True)),
                ('average', models.FloatField(help_text='Vacabularty size of MP', null=True, verbose_name='average', blank=True)),
                ('maximum', models.FloatField(help_text='Max of MP vacabularty size ', null=True, verbose_name='max', blank=True)),
                ('maxMP', models.ForeignKey(related_name='maxUniqueWords', blank=True, to='parlaposlanci.Person', help_text='Person who has max vacabularty size', null=True)),
                ('person', models.ForeignKey(related_name='uniqueWords', blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='vocabularysize',
            name='maxMP',
            field=models.ForeignKey(related_name='maxVocabulary', blank=True, to='parlaposlanci.Person', help_text='Person who has max vacabularty size', null=True),
        ),
        migrations.AlterField(
            model_name='vocabularysize',
            name='person',
            field=models.ForeignKey(related_name='VocabularySizes', blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
    ]
