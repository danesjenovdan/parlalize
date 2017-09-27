# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0036_question_author_org'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoteNote',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('parlaseje.vote',),
        ),
        migrations.AddField(
            model_name='vote',
            name='note',
            field=tinymce.models.HTMLField(null=True, blank=True),
        ),
    ]
