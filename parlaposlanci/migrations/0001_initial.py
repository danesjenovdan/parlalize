# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import parlaposlanci.models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AverageNumberOfSpeechesPerSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('score', models.FloatField(help_text='MP score', null=True, blank=True)),
                ('average', models.FloatField(help_text='Average score', null=True, blank=True)),
                ('maximum', models.FloatField(help_text='Maximum score', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CutVotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('this_for', models.IntegerField()),
                ('this_against', models.IntegerField()),
                ('this_abstain', models.IntegerField()),
                ('coalition_for', models.IntegerField()),
                ('coalition_against', models.IntegerField()),
                ('coalition_abstain', models.IntegerField()),
                ('coalition_for_max', models.IntegerField()),
                ('coalition_against_max', models.IntegerField()),
                ('coalition_abstain_max', models.IntegerField()),
                ('coalition_for_max_person', models.CharField(max_length=500)),
                ('coalition_against_max_person', models.CharField(max_length=500)),
                ('coalition_abstain_max_person', models.CharField(max_length=500)),
                ('opposition_for', models.IntegerField()),
                ('opposition_against', models.IntegerField()),
                ('opposition_abstain', models.IntegerField()),
                ('opposition_for_max', models.IntegerField()),
                ('opposition_against_max', models.IntegerField()),
                ('opposition_abstain_max', models.IntegerField()),
                ('opposition_for_max_person', models.CharField(max_length=500)),
                ('opposition_against_max_person', models.CharField(max_length=500)),
                ('opposition_abstain_max_person', models.CharField(max_length=500)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EqualVoters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('votes1', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters1', blank=True)),
                ('votes2', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters2', blank=True)),
                ('votes3', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters3', blank=True)),
                ('votes4', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters4', blank=True)),
                ('votes5', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters5', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LastActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('date', parlaposlanci.models.PopoloDateTimeField(help_text='date of activity', null=True, verbose_name='date of activity', blank=True)),
                ('session_id', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
                ('vote_name', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
                ('typee', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
                ('activity_id', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
                ('option', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
                ('result', models.TextField(help_text='type of activity', null=True, verbose_name='type of activity', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LessEqualVoters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('votes1', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters1', blank=True)),
                ('votes2', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters2', blank=True)),
                ('votes3', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters3', blank=True)),
                ('votes4', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters4', blank=True)),
                ('votes5', models.FloatField(help_text='EqualVoters', null=True, verbose_name='EqualVoters5', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MPStaticGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('groupid', models.IntegerField()),
                ('groupname', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MPStaticPL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('voters', models.IntegerField(help_text='Number of voters', null=True, blank=True)),
                ('age', models.IntegerField(help_text="Person's age.", null=True, blank=True)),
                ('mandates', models.IntegerField(help_text='Number of mandates', null=True, blank=True)),
                ('party_id', models.IntegerField(help_text='Parladata party id', null=True, blank=True)),
                ('acronym', models.TextField(help_text="Parliament group's acronym", null=True, blank=True)),
                ('education', models.TextField(help_text="Person's education", null=True, blank=True)),
                ('previous_occupation', models.TextField(help_text="Person's previous occupation", null=True, blank=True)),
                ('name', models.TextField(help_text='Name', null=True, blank=True)),
                ('district', models.TextField(help_text='Voting district name.', null=True, blank=True)),
                ('facebook', models.TextField(default=None, help_text='Facebook profile URL', null=True, blank=True)),
                ('twitter', models.TextField(default=None, help_text='Twitter profile URL', null=True, blank=True)),
                ('linkedin', models.TextField(default=None, help_text='Linkedin profile URL', null=True, blank=True)),
                ('party_name', models.TextField(help_text='Party name', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MPsWhichFitsToPG',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NumberOfSpeechesPerSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('person_value', models.IntegerField(help_text='Number of speeches of this MP', null=True, verbose_name='Number of speeches of this MP', blank=True)),
                ('average', models.IntegerField(help_text='Average of MP speeches per session', null=True, verbose_name='average', blank=True)),
                ('maximum', models.IntegerField(help_text='Max of MP speeches per session', null=True, verbose_name='max', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text="A person's preferred full name", max_length=128, null=True, verbose_name='name', blank=True)),
                ('pg', models.CharField(help_text='Parlament group of MP', max_length=128, null=True, verbose_name='parlament group')),
                ('id_parladata', models.IntegerField(help_text='id parladata', null=True, verbose_name='parladata id', blank=True)),
                ('image', models.URLField(help_text='A URL of a head shot', null=True, verbose_name='image', blank=True)),
                ('actived', models.CharField(help_text='Yes if MP is actived or no if it is not', max_length=128, null=True, verbose_name='actived')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Presence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('person_value', models.IntegerField(help_text='Presence of this MP', null=True, verbose_name='Presence of this MP', blank=True)),
                ('average', models.IntegerField(help_text='Average of MP attended sessions', null=True, verbose_name='average', blank=True)),
                ('maximum', models.IntegerField(help_text='Max of MP attended sessions', null=True, verbose_name='max', blank=True)),
                ('maxMP', models.ForeignKey(related_name='children_', blank=True, to='parlaposlanci.Person', help_text='Person who has max presence of sessions', null=True)),
                ('person', models.ForeignKey(related_name='children', blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpeakingStyle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('problematicno_score', models.IntegerField(help_text='Problematicno besedje score.')),
                ('privzdignjeno_score', models.IntegerField(help_text='Privzdignjeno besedje score.')),
                ('preprosto_score', models.IntegerField(help_text='Preprosto besedje score.')),
                ('problematicno_avg', models.IntegerField(help_text='Problematicno besedje average score.')),
                ('privzdignjeno_avg', models.IntegerField(help_text='Privzdignjeno besedje average score.')),
                ('preprosto_avg', models.IntegerField(help_text='Preprosto besedje average score.')),
                ('person', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpokenWords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('score', models.IntegerField(help_text='SW of this MP', null=True, verbose_name='SW of this MP', blank=True)),
                ('average', models.IntegerField(help_text='Average of MP attended sessions', null=True, verbose_name='average', blank=True)),
                ('maximum', models.IntegerField(help_text='Max of MP attended sessions', null=True, verbose_name='max', blank=True)),
                ('maxMP', models.ForeignKey(related_name='childrenSW_', blank=True, to='parlaposlanci.Person', help_text='Person who has max spoken words', null=True)),
                ('person', models.ForeignKey(related_name='childrenSW', blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StyleScores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('problematicno', models.FloatField(help_text='Problematicno score of this MP', null=True, verbose_name='Problematicno style score of this MP', blank=True)),
                ('privzdignjeno', models.FloatField(help_text='Privzdignjeno style score of this MP', null=True, verbose_name='Privzdignjeno style score of this MP', blank=True)),
                ('preprosto', models.FloatField(help_text='Preprosto style score of this MP', null=True, verbose_name='Preprosto style score of this MP', blank=True)),
                ('problematicno_average', models.FloatField(help_text='Problematicno average style score', null=True, verbose_name='Problematicno average style score', blank=True)),
                ('privzdignjeno_average', models.FloatField(help_text='Privzdignjeno average style score', null=True, verbose_name='Privzdignjeno average style score', blank=True)),
                ('preprosto_average', models.FloatField(help_text='Preprosto average style score', null=True, verbose_name='Preprosto average style score', blank=True)),
                ('person', models.ForeignKey(related_name='childrenStSc', blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tfidf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('person', models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VocabularySize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('score', models.IntegerField(help_text='Vacabularty size of this MP', null=True, verbose_name='Vacabularty size of this MP', blank=True)),
                ('average', models.IntegerField(help_text='Vacabularty size of MP', null=True, verbose_name='average', blank=True)),
                ('maximum', models.IntegerField(help_text='Max of MP vacabularty size ', null=True, verbose_name='max', blank=True)),
                ('maxMP', models.ForeignKey(related_name='childrenVacSiz', blank=True, to='parlaposlanci.Person', help_text='Person who has max vacabularty size', null=True)),
                ('person', models.ForeignKey(related_name='childrenVS', blank=True, to='parlaposlanci.Person', help_text='MP', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='numberofspeechespersession',
            name='maxMP',
            field=models.ForeignKey(related_name='childrenNOSPS', blank=True, to='parlaposlanci.Person', help_text='Person who has max speeches per session', null=True),
        ),
        migrations.AddField(
            model_name='numberofspeechespersession',
            name='person',
            field=models.ForeignKey(related_name='speaker', blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
        migrations.AddField(
            model_name='mpswhichfitstopg',
            name='person',
            field=models.ForeignKey(related_name='childrenMPWPG', blank=True, to='parlaposlanci.Person', help_text='MP1', null=True),
        ),
        migrations.AddField(
            model_name='mpstaticpl',
            name='person',
            field=models.ForeignKey(help_text='Person foreign key relationship', to='parlaposlanci.Person'),
        ),
        migrations.AddField(
            model_name='mpstaticgroup',
            name='person',
            field=models.ForeignKey(help_text='Person foreign key to MPStaticPL', to='parlaposlanci.MPStaticPL'),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person',
            field=models.ForeignKey(related_name='childrenLEWT', blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person1',
            field=models.ForeignKey(related_name='childrenLEW1', blank=True, to='parlaposlanci.Person', help_text='MP1', null=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person2',
            field=models.ForeignKey(related_name='childrenLEW2', blank=True, to='parlaposlanci.Person', help_text='MP2', null=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person3',
            field=models.ForeignKey(related_name='childrenLEW3', blank=True, to='parlaposlanci.Person', help_text='MP3', null=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person4',
            field=models.ForeignKey(related_name='childrenLEW4', blank=True, to='parlaposlanci.Person', help_text='MP4', null=True),
        ),
        migrations.AddField(
            model_name='lessequalvoters',
            name='person5',
            field=models.ForeignKey(related_name='childrenLEW5', blank=True, to='parlaposlanci.Person', help_text='MP5', null=True),
        ),
        migrations.AddField(
            model_name='lastactivity',
            name='person',
            field=models.ForeignKey(related_name='childrenLA', blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person',
            field=models.ForeignKey(related_name='childrenEWT', blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person1',
            field=models.ForeignKey(related_name='childrenEW1', blank=True, to='parlaposlanci.Person', help_text='MP1', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person2',
            field=models.ForeignKey(related_name='childrenEW2', blank=True, to='parlaposlanci.Person', help_text='MP2', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person3',
            field=models.ForeignKey(related_name='childrenEW3', blank=True, to='parlaposlanci.Person', help_text='MP3', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person4',
            field=models.ForeignKey(related_name='childrenEW4', blank=True, to='parlaposlanci.Person', help_text='MP4', null=True),
        ),
        migrations.AddField(
            model_name='equalvoters',
            name='person5',
            field=models.ForeignKey(related_name='childrenEW5', blank=True, to='parlaposlanci.Person', help_text='MP5', null=True),
        ),
        migrations.AddField(
            model_name='cutvotes',
            name='person',
            field=models.ForeignKey(to='parlaposlanci.Person'),
        ),
        migrations.AddField(
            model_name='averagenumberofspeechespersession',
            name='maxMP',
            field=models.ForeignKey(related_name='max_person', blank=True, to='parlaposlanci.Person', help_text='Maximum MP', null=True),
        ),
        migrations.AddField(
            model_name='averagenumberofspeechespersession',
            name='person',
            field=models.ForeignKey(blank=True, to='parlaposlanci.Person', help_text='MP', null=True),
        ),
    ]
