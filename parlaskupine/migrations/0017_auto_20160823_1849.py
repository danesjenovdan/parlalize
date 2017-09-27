# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0016_workingbodies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgstatic',
            name='headOfPG',
            field=models.ForeignKey(related_name='PGStaticH', to='parlaposlanci.Person', help_text='Head of MP', null=True),
        ),
        migrations.AlterField(
            model_name='pgstatic',
            name='viceOfPG',
            field=models.ForeignKey(related_name='PGStaticV', to='parlaposlanci.Person', help_text='Vice of MP', null=True),
        ),
    ]
