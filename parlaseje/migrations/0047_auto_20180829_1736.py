# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-29 17:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0036_auto_20180820_1140'),
        ('parlaskupine', '0031_auto_20180820_1140'),
        ('parlaseje', '0046_auto_20180820_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='persons',
            field=models.ManyToManyField(blank=True, help_text='MP', to='parlaposlanci.Person'),
        ),
        migrations.AddField(
            model_name='question',
            name='author_orgs',
            field=models.ManyToManyField(blank=True, help_text='Author organizations', to='parlaskupine.Organization'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='person',
            field=models.ForeignKey(blank=True, help_text='MP', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activitys', to='parlaposlanci.Person'),
        ),
        migrations.AlterField(
            model_name='legislation',
            name='result',
            field=models.CharField(blank=True, choices=[(b'enacted', b'enacted'), (b'submitted', b'submitted'), (b'rejected', b'rejected'), (b'retracted', b'retracted'), (b'adopted', b'adopted'), (b'received', b'received'), (b'in_procedure', b'in_procedure')], help_text=b'result of law', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='legislation',
            name='status',
            field=models.CharField(blank=True, choices=[(b'enacted', b'enacted'), (b'submitted', b'submitted'), (b'rejected', b'rejected'), (b'retracted', b'retracted'), (b'adopted', b'adopted'), (b'received', b'received'), (b'in_procedure', b'in_procedure')], default=b'enacted', help_text=b'result of law', max_length=255, null=True),
        ),
    ]
