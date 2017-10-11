# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0032_question_recipient_persons_static'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='recipient_organizations',
            field=models.ManyToManyField(help_text=b"Recipient organizations (if it's an organization).", related_name='questions_org', to='parlaskupine.Organization', blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='recipient_persons',
            field=models.ManyToManyField(help_text=b"Recipient persons (if it's a person).", related_name='questions', to='parlaposlanci.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='recipient_persons_static',
            field=models.ManyToManyField(help_text=b"Recipient persons (if it's a person).", related_name='questions_static', to='parlaposlanci.MinisterStatic', blank=True),
        ),
    ]
