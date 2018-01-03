# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0031_mpstaticpl_education_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpstaticpl',
            name='party_id',
            field=models.ForeignKey(related_name='static_party', to='parlaskupine.Organization', help_text='Parladata party id', null=True),
        ),
    ]
