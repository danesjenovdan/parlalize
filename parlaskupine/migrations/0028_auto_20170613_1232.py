# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0027_intradisunion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intradisunion',
            name='vote',
            field=models.ForeignKey(related_name='vote_intradisunion', blank=True, to='parlaseje.Vote', help_text='Vote', null=True),
        ),
    ]
