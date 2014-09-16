# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rh', '0001_initial'),
        ('cadastro', '0002_auto_20140916_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowUpDeContrato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField()),
                ('porcentagem_execucao', models.DecimalField(max_digits=3, decimal_places=0)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'ordering': ['-criado'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAcessoProgramacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso \xe0 Programa\xe7\xe3o',
                'verbose_name_plural': 'Perfis de Acesso \xe0 Programa\xe7\xe3o',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TarefaDeProgramacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status_execucao', models.CharField(default=b'naoiniciado', max_length=100, verbose_name='Status da Execu\xe7\xe3o da Tarefa de Programa\xe7\xe3o', choices=[(b'naoiniciado', 'N\xe3o Iniciado'), (b'emandamento', 'Em Andamento'), (b'pendente', 'Pendente'), (b'finalizado', 'Finalizado')])),
                ('porcentagem_execucao', models.DecimalField(default=0, max_digits=3, decimal_places=0)),
                ('aguardando_cliente', models.BooleanField(default=False)),
                ('data_aguardando_cliente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_emandamento', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_pendente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_retorno_cliente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_finalizado', models.DateTimeField(null=True, blank=True)),
                ('data_programada', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('cliente', models.ForeignKey(blank=True, to='cadastro.Cliente', null=True)),
                ('contrato', models.ForeignKey(blank=True, to='comercial.ContratoFechado', null=True)),
                ('criado_por', models.ForeignKey(related_name=b'tarefa_de_programacao_adicionado_set', to='rh.Funcionario')),
                ('funcionarios_participantes', models.ManyToManyField(related_name=b'contratos_participantes_programacao', null=True, to='rh.Funcionario', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='followupdecontrato',
            name='contrato',
            field=models.ForeignKey(to='programacao.TarefaDeProgramacao'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='followupdecontrato',
            name='criado_por',
            field=models.ForeignKey(related_name=b'followup_contrato_adicionado_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
    ]
