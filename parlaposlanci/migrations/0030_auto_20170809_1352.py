# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0029_auto_20170712_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='MismatchOfPG',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('created_for', models.DateField(help_text='date of analize', null=True, verbose_name='date of activity', blank=True)),
                ('data', models.FloatField(help_text='Percentage of the same vote as his parlimentary group', null=True, verbose_name='Percentage of the same vote as his parlimentary group', blank=True)),
                ('person', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='mpstaticpl',
            name='person',
            field=models.ForeignKey(related_name='static_data', to='parlaposlanci.Person', help_text='Person foreign key relationship'),
        ),
    ]
