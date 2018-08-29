# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0035_mpstaticpl_birth_date'),
        ('parlaseje', '0044_speech_agenda_item_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='amendment_of_person',
            field=models.ManyToManyField(related_name='amendments', to='parlaposlanci.Person'),
        ),
    ]
