# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('cadastro', '0002_auto_20140916_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GrupoAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocalAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('cep', models.CharField(max_length=100, verbose_name='CEP', blank=True)),
                ('rua', models.CharField(max_length=500, verbose_name='Rua', blank=True)),
                ('numero', models.CharField(max_length=100, verbose_name='N\xfamero', blank=True)),
                ('complemento', models.CharField(max_length=200, verbose_name='Complemento', blank=True)),
                ('bairro', models.ForeignKey(to='cadastro.Bairro')),
                ('cidade', models.ForeignKey(to='cadastro.Cidade')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParticipaoDiaDeAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('participacao_efetiva', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAluno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilProfessor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('funcionario', models.OneToOneField(to='rh.Funcionario')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnidadeDeAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inicio', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('fim', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('aula', models.ForeignKey(to='treinamento.Aula')),
                ('professor', models.ForeignKey(to='treinamento.PerfilProfessor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='participaodiadeaula',
            name='aluno',
            field=models.ForeignKey(to='treinamento.PerfilAluno'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participaodiadeaula',
            name='dia_de_aula',
            field=models.ForeignKey(to='treinamento.UnidadeDeAula'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participaodiadeaula',
            name='professor',
            field=models.ForeignKey(to='treinamento.PerfilProfessor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aula',
            name='alunos_inscritos',
            field=models.ManyToManyField(to='treinamento.PerfilAluno'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aula',
            name='grupo',
            field=models.ForeignKey(to='treinamento.GrupoAula'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aula',
            name='local',
            field=models.ForeignKey(to='treinamento.LocalAula'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aula',
            name='professor',
            field=models.ForeignKey(to='treinamento.PerfilProfessor'),
            preserve_default=True,
        ),
    ]
