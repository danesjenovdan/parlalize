# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.TextField(help_text='A primary name, e.g. a legally recognized name', verbose_name='name')),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('classification', models.TextField(help_text='Organization calssification.', null=True, verbose_name='Classification', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PercentOFAttendedSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('organization_value', models.IntegerField(help_text='Presence of this PG', null=True, verbose_name='Presence of this PG', blank=True)),
                ('average', models.IntegerField(help_text='Average of PG attended sessions', null=True, verbose_name='average', blank=True)),
                ('maximum', models.IntegerField(help_text='Max of PG attended sessions', null=True, verbose_name='max', blank=True)),
                ('maxPG', models.ForeignKey(related_name='childrenMaxMP', blank=True, to='parlaskupine.Organization', help_text='PG who has max prfesence of sessions', null=True)),
                ('organization', models.ForeignKey(related_name='childrenPG', blank=True, to='parlaskupine.Organization', help_text='PG', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PGStatic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('numberOfSeats', models.IntegerField(help_text='Number of seats in parlament of PG', null=True, blank=True)),
                ('allVoters', models.IntegerField(help_text='Number of voters', null=True, blank=True)),
                ('facebook', models.TextField(default=None, help_text='Facebook profile URL', null=True, blank=True)),
                ('twitter', models.TextField(default=None, help_text='Twitter profile URL', null=True, blank=True)),
                ('email', models.TextField(default=None, help_text='email profile URL', null=True, blank=True)),
                ('headOfPG', models.ForeignKey(related_name='PGStaticH', to='parlaposlanci.Person', help_text='Head of MP')),
                ('organization', models.ForeignKey(help_text='Organization foreign key relationship', to='parlaskupine.Organization')),
                ('viceOfPG', models.ForeignKey(related_name='PGStaticV', to='parlaposlanci.Person', help_text='Vice of MP')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
