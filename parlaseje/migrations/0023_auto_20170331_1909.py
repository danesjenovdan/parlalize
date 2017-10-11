# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0027_ministerstatic'),
        ('parlaskupine', '0026_presencethroughtime'),
        ('parlaseje', '0022_vote_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='recipient_organization',
        ),
        migrations.RemoveField(
            model_name='question',
            name='recipient_person',
        ),
        migrations.AddField(
            model_name='question',
            name='recipient_organizations',
            field=models.ManyToManyField(help_text=b"Recipient organizations (if it's an organization).", related_name='questions_org', null=True, to='parlaskupine.Organization', blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='recipient_persons',
            field=models.ManyToManyField(help_text=b"Recipient persons (if it's a person).", related_name='questions', null=True, to='parlaposlanci.Person', blank=True),
        ),
    ]
