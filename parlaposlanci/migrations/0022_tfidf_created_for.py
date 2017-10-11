# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0021_person_has_function'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfidf',
            name='created_for',
            field=models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True),
        ),
    ]
