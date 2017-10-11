# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0003_auto_20160221_1528'),
        ('parlaskupine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviationInOrganization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True)),
                ('votes1', models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation1', blank=True)),
                ('votes2', models.FloatField(help_text='MatchingThem', null=True, verbose_name='daviation2', blank=True)),
                ('organization', models.ForeignKey(related_name='childrenD', blank=True, to='parlaskupine.Organization', help_text='PG', null=True)),
                ('person1', models.ForeignKey(related_name='childrenD1', blank=True, to='parlaposlanci.Person', help_text='D1', null=True)),
                ('person2', models.ForeignKey(related_name='childrenD2', blank=True, to='parlaposlanci.Person', help_text='D2', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LessMatchingThem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of activity', null=True, verbose_name='date of analize', blank=True)),
                ('votes1', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem1', blank=True)),
                ('votes2', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem2', blank=True)),
                ('votes3', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem3', blank=True)),
                ('votes4', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem4', blank=True)),
                ('votes5', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem5', blank=True)),
                ('organization', models.ForeignKey(related_name='childrenLMT', blank=True, to='parlaskupine.Organization', help_text='PG', null=True)),
                ('person1', models.ForeignKey(related_name='childrenLMT1', blank=True, to='parlaposlanci.Person', help_text='MP1', null=True)),
                ('person2', models.ForeignKey(related_name='childrenLMT2', blank=True, to='parlaposlanci.Person', help_text='MP2', null=True)),
                ('person3', models.ForeignKey(related_name='childrenLMT3', blank=True, to='parlaposlanci.Person', help_text='MP3', null=True)),
                ('person4', models.ForeignKey(related_name='childrenLMT4', blank=True, to='parlaposlanci.Person', help_text='MP4', null=True)),
                ('person5', models.ForeignKey(related_name='childrenLMT5', blank=True, to='parlaposlanci.Person', help_text='MP5', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MostMatchingThem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of analize', blank=True)),
                ('votes1', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem1', blank=True)),
                ('votes2', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem2', blank=True)),
                ('votes3', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem3', blank=True)),
                ('votes4', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem4', blank=True)),
                ('votes5', models.FloatField(help_text='MatchingThem', null=True, verbose_name='MatchingThem5', blank=True)),
                ('organization', models.ForeignKey(related_name='childrenMMT', blank=True, to='parlaskupine.Organization', help_text='PG', null=True)),
                ('person1', models.ForeignKey(related_name='childrenMMT1', blank=True, to='parlaposlanci.Person', help_text='MP1', null=True)),
                ('person2', models.ForeignKey(related_name='childrenMMT2', blank=True, to='parlaposlanci.Person', help_text='MP2', null=True)),
                ('person3', models.ForeignKey(related_name='childrenMMT3', blank=True, to='parlaposlanci.Person', help_text='MP3', null=True)),
                ('person4', models.ForeignKey(related_name='childrenMMT4', blank=True, to='parlaposlanci.Person', help_text='MP4', null=True)),
                ('person5', models.ForeignKey(related_name='childrenMMT5', blank=True, to='parlaposlanci.Person', help_text='MP5', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
