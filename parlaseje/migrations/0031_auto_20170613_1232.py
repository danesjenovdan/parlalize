# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('parlaseje', '0030_vote_has_outlier_voters'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoteDetailed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('motion', models.TextField(help_text=b'The motion for which the vote took place', null=True, blank=True)),
                ('created_for', models.DateField(help_text='date of vote', null=True, verbose_name='date of vote', blank=True)),
                ('votes_for', models.IntegerField(help_text=b'Number of votes for', null=True, blank=True)),
                ('against', models.IntegerField(help_text=b'Number votes againt', null=True, blank=True)),
                ('abstain', models.IntegerField(help_text=b'Number votes abstain', null=True, blank=True)),
                ('not_present', models.IntegerField(help_text=b'Number of MPs that warent on the session', null=True, blank=True)),
                ('result', models.NullBooleanField(default=False, help_text=b'The result of the vote')),
                ('pgs_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('pgs_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_yes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_no', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_np', jsonfield.fields.JSONField(null=True, blank=True)),
                ('mp_kvor', jsonfield.fields.JSONField(null=True, blank=True)),
                ('session', models.ForeignKey(related_name='in_session_for_VG', blank=True, to='parlaseje.Session', help_text='Session ', null=True)),
                ('vote', models.ForeignKey(related_name='vote_of_graph', blank=True, to='parlaseje.Vote', help_text='Vote', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='AverageSpeeches',
        ),
        migrations.RemoveField(
            model_name='vote_graph',
            name='session',
        ),
        migrations.RemoveField(
            model_name='vote_graph',
            name='vote',
        ),
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.TextField(help_text=b'Words spoken', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='speech',
            name='content',
            field=models.TextField(help_text=b'Words spoken', null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='Vote_graph',
        ),
    ]
