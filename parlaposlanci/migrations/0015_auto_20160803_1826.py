# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parlaposlanci', '0014_mpstaticpl_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_absent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_absent_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_abstain',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_abstain_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_against',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_against_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_for',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='coalition_for_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_absent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_absent_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_abstain',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_abstain_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_against',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_against_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_for',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='opposition_for_max',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='this_absent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='this_abstain',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='this_against',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='cutvotes',
            name='this_for',
            field=models.FloatField(),
        ),
    ]
