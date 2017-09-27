# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0026_presencethroughtime'),
        ('parlaposlanci', '0026_memberslist_presencethroughtime'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinisterStatic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('age', models.IntegerField(help_text="Person's age.", null=True, blank=True)),
                ('acronym', models.TextField(help_text="Parliament group's acronym", null=True, blank=True)),
                ('education', models.TextField(help_text="Person's education", null=True, blank=True)),
                ('previous_occupation', models.TextField(help_text="Person's previous occupation", null=True, blank=True)),
                ('name', models.TextField(help_text='Name', null=True, blank=True)),
                ('district', jsonfield.fields.JSONField(help_text='Voting district name.', null=True, blank=True)),
                ('facebook', models.TextField(default=None, help_text='Facebook profile URL', null=True, blank=True)),
                ('twitter', models.TextField(default=None, help_text='Twitter profile URL', null=True, blank=True)),
                ('linkedin', models.TextField(default=None, help_text='Linkedin profile URL', null=True, blank=True)),
                ('party_name', models.TextField(help_text='Party name', null=True, blank=True)),
                ('gov_id', models.CharField(help_text='The ID of the official on the government website.', max_length=128, null=True, verbose_name='gov id')),
                ('gender', models.CharField(default=b'f', help_text='Gender', max_length=1)),
                ('ministry', models.ForeignKey(related_name='ministry_ministers', blank=True, to='parlaskupine.Organization', help_text='Parladata party id', null=True)),
                ('party', models.ForeignKey(related_name='party_ministers', blank=True, to='parlaskupine.Organization', help_text='Parladata party id', null=True)),
                ('person', models.ForeignKey(help_text='Person foreign key relationship', to='parlaposlanci.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
