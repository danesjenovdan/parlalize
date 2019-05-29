# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-29 10:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
         ('parlaposlanci', '0037_mpstaticpl_points')
    ]

    database_operations = [
        migrations.AlterModelTable('Compass', 'parlaskupine_compass')
    ]

    state_operations = [
        migrations.DeleteModel('Compass')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]