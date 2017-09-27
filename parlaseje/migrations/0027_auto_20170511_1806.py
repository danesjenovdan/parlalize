# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import parlaseje.models


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0026_presencethroughtime'),
        ('parlaseje', '0026_auto_20170510_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='ballot',
            name='org_voter',
            field=models.ForeignKey(related_name='OrganizationVoter', blank=True, to='parlaskupine.Organization', help_text='Organization voter', null=True),
        ),
    ]
