# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0025_numberofquestions'),
        ('parlaskupine', '0025_numberofquestions'),
        ('parlaseje', '0018_auto_20161212_2256'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('activity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('content_link', models.URLField(help_text=b'Words spoken', max_length=350)),
                ('title', models.TextField(help_text=b'Words spoken')),
                ('recipient_text', models.TextField(help_text=b'Recipient name as written on dz-rs.si', null=True, blank=True)),
                ('recipient_organization', models.ForeignKey(related_name='questions_org', blank=True, to='parlaskupine.Organization', help_text=b"Recipient organization (if it's an organization).", null=True)),
                ('recipient_person', models.ForeignKey(related_name='questions', blank=True, to='parlaposlanci.Person', help_text=b"Recipient person (if it's a person).", null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity',),
        ),
        migrations.AddField(
            model_name='speech',
            name='valid_from',
            field=models.DateTimeField(default=None, help_text='row valid from', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='speech',
            name='valid_to',
            field=models.DateTimeField(default=None, help_text='row valid to', null=True, blank=True),
        ),
    ]
