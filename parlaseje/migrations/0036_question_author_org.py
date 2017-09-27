# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaskupine', '0029_auto_20170706_1641'),
        ('parlaseje', '0035_auto_20170712_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='author_org',
            field=models.ForeignKey(related_name='AuthorOrg', blank=True, to='parlaskupine.Organization', help_text='Author organization', null=True),
        ),
    ]
