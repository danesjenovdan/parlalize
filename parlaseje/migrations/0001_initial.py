# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-18 14:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
import parlaseje.models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbsentMPs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('absentMPs', jsonfield.fields.JSONField(blank=True, null=True)),
                ('created_for', models.DateField(blank=True, help_text='date of vote', null=True, verbose_name='date of vote')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('id_parladata', models.IntegerField(blank=True, db_index=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('start_time', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'Start time', null=True)),
                ('end_time', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'End time', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AgendaItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('title', models.CharField(blank=True, help_text=b'Title of AgnedaItem', max_length=1024, null=True)),
                ('id_parladata', models.IntegerField(blank=True, help_text='id parladata', null=True, verbose_name='parladata id')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AmendmentOfOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Debate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('date', models.DateField(blank=True, help_text='date of debate', null=True, verbose_name='date of debate')),
                ('id_parladata', models.IntegerField(blank=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('agenda_item', models.ManyToManyField(blank=True, help_text='AgendaItem ', related_name='debates', to='parlaseje.AgendaItem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Legislation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('text', models.TextField(blank=True, help_text=b'The text of the motion', null=True)),
                ('epa', models.CharField(blank=True, help_text=b'EPA number', max_length=255, null=True)),
                ('mdt', models.CharField(blank=True, help_text=b'Working body', max_length=255, null=True)),
                ('mdt_fk', models.CharField(blank=True, help_text=b'Working body', max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[(b'enacted', b'enacted'), (b'submitted', b'submitted'), (b'rejected', b'rejected'), (b'retracted', b'retracted'), (b'adopted', b'adopted'), (b'received', b'received'), (b'in_procedure', b'in_procedure')], default=b'enacted', help_text=b'result of law', max_length=255, null=True)),
                ('result', models.CharField(blank=True, choices=[(b'enacted', b'enacted'), (b'submitted', b'submitted'), (b'rejected', b'rejected'), (b'retracted', b'retracted'), (b'adopted', b'adopted'), (b'received', b'received'), (b'in_procedure', b'in_procedure')], help_text=b'result of law', max_length=255, null=True)),
                ('id_parladata', models.IntegerField(blank=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('proposer_text', models.TextField(blank=True, help_text=b'Proposer of law', null=True)),
                ('procedure_phase', models.CharField(blank=True, help_text=b'Procedure phase of law', max_length=255, null=True)),
                ('procedure', models.CharField(blank=True, help_text=b'Procedure of law', max_length=255, null=True)),
                ('type_of_law', models.CharField(blank=True, max_length=255, null=True)),
                ('note', tinymce.models.HTMLField(blank=True, null=True)),
                ('extra_note', tinymce.models.HTMLField(blank=True, null=True)),
                ('abstractVisible', models.BooleanField(default=False, help_text=b'Is abstract visible')),
                ('date', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'Time of last procudure', null=True)),
                ('is_exposed', models.BooleanField(default=False, help_text=b'Is abstract visible')),
                ('icon', models.CharField(blank=True, max_length=255, null=True)),
                ('procedure_ended', models.BooleanField(default=False, help_text=b'Procedure phase of law')),
                ('classification', models.CharField(blank=True, help_text=b'Classification of law', max_length=255, null=True)),
                ('has_discussion', models.BooleanField(default=False, help_text=b'Legislation has discusion')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PresenceOfPG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('presence', jsonfield.fields.JSONField(blank=True, null=True)),
                ('created_for', models.DateField(blank=True, help_text='date of analize', null=True, verbose_name='date of activity')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('quoted_text', models.TextField(blank=True, help_text='text quoted in a speech', null=True, verbose_name='quoted text')),
                ('first_char', models.IntegerField(blank=True, help_text='index of first character of quote string', null=True)),
                ('last_char', models.IntegerField(blank=True, help_text='index of last character of quote string', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('name', models.CharField(blank=True, help_text='Session name', max_length=512, null=True, verbose_name='name')),
                ('date', parlaseje.models.PopoloDateTimeField(blank=True, help_text='date of session', null=True, verbose_name='date of session')),
                ('id_parladata', models.IntegerField(blank=True, db_index=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('mandate', models.CharField(blank=True, help_text='Mandate name', max_length=128, null=True, verbose_name='mandate name')),
                ('start_time', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'Start time', null=True, verbose_name='start time of session')),
                ('end_time', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'End time', null=True, verbose_name='end time of session')),
                ('actived', models.CharField(blank=True, help_text='Yes if PG is actived or no if it is not', max_length=128, null=True, verbose_name='actived')),
                ('classification', models.CharField(blank=True, help_text='An organization category, e.g. committee', max_length=128, null=True, verbose_name='classification')),
                ('gov_id', models.TextField(blank=True, help_text=b'Gov website ID.', null=True)),
                ('in_review', models.BooleanField(default=False, help_text=b'Is session in review?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_parladata', models.IntegerField(blank=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('name', models.TextField(blank=True, help_text='tag name', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tfidf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('created_for', models.DateField(blank=True, help_text='date of analize', null=True, verbose_name='date of activity')),
                ('is_visible', models.BooleanField(default=True, verbose_name='is visible')),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
                ('session', models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tfidf', to='parlaseje.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('created_for', models.DateField(blank=True, help_text='date of vote', null=True, verbose_name='date of vote')),
                ('motion', models.TextField(blank=True, help_text=b'The motion for which the vote took place', null=True)),
                ('tags', jsonfield.fields.JSONField(blank=True, null=True)),
                ('votes_for', models.IntegerField(blank=True, help_text=b'Number of votes for', null=True)),
                ('against', models.IntegerField(blank=True, help_text=b'Number votes againt', null=True)),
                ('abstain', models.IntegerField(blank=True, help_text=b'Number votes abstain', null=True)),
                ('not_present', models.IntegerField(blank=True, help_text=b'Number of MPs that warent on the session', null=True)),
                ('result', models.NullBooleanField(default=False, help_text=b'The result of the vote')),
                ('id_parladata', models.IntegerField(blank=True, db_index=True, help_text='id parladata', null=True, verbose_name='parladata id')),
                ('document_url', jsonfield.fields.JSONField(blank=True, null=True)),
                ('start_time', parlaseje.models.PopoloDateTimeField(blank=True, help_text=b'Start time', null=True)),
                ('is_outlier', models.NullBooleanField(default=False, help_text=b'is outlier')),
                ('has_outlier_voters', models.NullBooleanField(default=False, help_text=b'has outlier voters')),
                ('intra_disunion', models.FloatField(default=0.0, help_text=b'intra disunion for all members')),
                ('abstractVisible', models.BooleanField(default=False, help_text=b'Is abstract visible')),
                ('note', tinymce.models.HTMLField(blank=True, null=True)),
                ('epa', models.CharField(blank=True, help_text=b'EPA number', max_length=255, null=True)),
                ('classification', models.CharField(blank=True, help_text=b'classification', max_length=255, null=True)),
                ('agenda_item', models.ManyToManyField(blank=True, help_text=b'Agenda item', related_name='votes', to='parlaseje.AgendaItem')),
                ('law', models.ForeignKey(blank=True, help_text='Legislation foreign key', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='parlaseje.Legislation')),
                ('session', models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='in_session', to='parlaseje.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote_analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='creation time')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='last modification time')),
                ('created_for', models.DateField(blank=True, help_text='date of vote', null=True, verbose_name='date of vote')),
                ('votes_for', models.IntegerField(blank=True, help_text=b'Number of votes for', null=True)),
                ('against', models.IntegerField(blank=True, help_text=b'Number votes againt', null=True)),
                ('abstain', models.IntegerField(blank=True, help_text=b'Number votes abstain', null=True)),
                ('not_present', models.IntegerField(blank=True, help_text=b'Number of MPs that warent on the session', null=True)),
                ('pgs_data', jsonfield.fields.JSONField(blank=True, null=True)),
                ('mp_yes', jsonfield.fields.JSONField(blank=True, null=True)),
                ('mp_no', jsonfield.fields.JSONField(blank=True, null=True)),
                ('mp_np', jsonfield.fields.JSONField(blank=True, null=True)),
                ('mp_kvor', jsonfield.fields.JSONField(blank=True, null=True)),
                ('coal_opts', jsonfield.fields.JSONField(blank=True, null=True)),
                ('oppo_opts', jsonfield.fields.JSONField(blank=True, null=True)),
                ('session', models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='in_session_for_VA', to='parlaseje.Session')),
                ('vote', models.ForeignKey(blank=True, help_text='Vote', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='parlaseje.Vote')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('option', models.CharField(blank=True, help_text=b'Yes, no, abstain', max_length=128, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('content_link', models.URLField(blank=True, help_text=b'Words spoken', max_length=350, null=True)),
                ('title', models.TextField(blank=True, help_text=b'Words spoken', null=True)),
                ('recipient_text', models.TextField(blank=True, help_text=b'Recipient name as written on dz-rs.si', null=True)),
                ('type_of_question', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity',),
        ),
        migrations.CreateModel(
            name='Speech',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='parlaseje.Activity')),
                ('valid_from', models.DateTimeField(blank=True, default=None, help_text='row valid from', null=True)),
                ('valid_to', models.DateTimeField(blank=True, default=None, help_text='row valid to', null=True)),
                ('content', models.TextField(blank=True, help_text=b'Words spoken', null=True)),
                ('order', models.IntegerField(blank=True, help_text=b'Order of speech', null=True)),
                ('agenda_item_order', models.IntegerField(blank=True, help_text=b'Order of speech', null=True)),
                ('the_order', models.IntegerField(blank=True, db_index=True, help_text=b'Absolute order on session', null=True)),
                ('debate', models.ForeignKey(blank=True, help_text='debate ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='speeches', to='parlaseje.Debate')),
            ],
            options={
                'abstract': False,
            },
            bases=('parlaseje.activity', models.Model),
        ),
        migrations.AddField(
            model_name='presenceofpg',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_presence', to='parlaseje.Session'),
        ),
        migrations.AddField(
            model_name='legislation',
            name='sessions',
            field=models.ManyToManyField(blank=True, help_text=b'The legislative session in which the motion was proposed', related_name='laws', to='parlaseje.Session'),
        ),
        migrations.AddField(
            model_name='amendmentoforg',
            name='vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parlaseje.Vote'),
        ),
        migrations.AddField(
            model_name='agendaitem',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agenda_items', to='parlaseje.Session'),
        ),
        migrations.AddField(
            model_name='activity',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parlaseje_activity_related', to='parlaseje.Session'),
        ),
        migrations.AddField(
            model_name='absentmps',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Session ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_absent', to='parlaseje.Session'),
        ),
        migrations.CreateModel(
            name='LegislationNote',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('parlaseje.legislation',),
        ),
        migrations.CreateModel(
            name='VoteNote',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('parlaseje.vote',),
        ),
        migrations.AddField(
            model_name='quote',
            name='speech',
            field=models.ForeignKey(help_text='the speech that is being quoted', on_delete=django.db.models.deletion.CASCADE, to='parlaseje.Speech'),
        ),
        migrations.AddField(
            model_name='ballot',
            name='vote',
            field=models.ForeignKey(blank=True, help_text='Vote', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vote', to='parlaseje.Vote'),
        ),
    ]
