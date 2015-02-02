# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastro', '0006_auto_20150125_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfilAcessoSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso \xe0 Solicita\xe7\xe3o',
                'verbose_name_plural': 'Perfis de Acesso \xe0s Solicita\xe7\xe3o',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Solicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contato', models.TextField(null=True, blank=True)),
                ('prioridade', models.IntegerField(default=5, choices=[(0, 'Baixa Prioridade'), (5, 'M\xe9dia Prioridade'), (10, 'Alta Prioridade')])),
                ('descricao', models.TextField(verbose_name='Descri\xe7\xe3o')),
                ('status', models.CharField(default=b'aberta', max_length=100, choices=[(b'aberta', 'Solicita\xe7\xe3o Aberta'), (b'analise', 'Solicita\xe7\xe3o em An\xe1lise'), (b'contato', 'Solicita\xe7\xe3o em Contato'), (b'visto', 'Solicita\xe7\xe3o em Visto'), (b'resolvida', 'Solicita\xe7\xe3o Resolvida'), (b'naoresolvido', 'Solicita\xe7\xe3o N\xe3o Resolvida')])),
                ('procede', models.BooleanField(default=True)),
                ('nao_procede_porque', models.TextField(blank=True)),
                ('providencia', models.TextField(blank=True)),
                ('prazo', models.DateField(default=datetime.datetime(2015, 2, 5, 19, 35, 58, 831491))),
                ('resolucao_final', models.TextField(verbose_name=b'Resolu\xc3\xa7\xc3\xa3o Final', blank=True)),
                ('resolucao_final_data', models.DateTimeField(null=True, blank=True)),
                ('correcao_iniciada', models.DateTimeField(null=True, blank=True)),
                ('contato_realizado', models.DateTimeField(null=True, blank=True)),
                ('visto_data', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('despachado_data', models.DateTimeField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('adicionado_por', models.ForeignKey(related_name=b'solicitacao_adicionada_set', blank=True, to='rh.Funcionario', null=True)),
                ('cliente', models.ForeignKey(blank=True, to='cadastro.Cliente', null=True)),
                ('departamento_direto', models.ForeignKey(related_name=b'solicitacao_direta_set', blank=True, to='rh.Departamento', null=True)),
                ('departamentos_afetados', models.ManyToManyField(related_name=b'solicitacao_afetada_set', null=True, to='rh.Departamento', blank=True)),
                ('despachado_por', models.ForeignKey(related_name=b'solicitacao_despachado_set', blank=True, to='rh.Funcionario', null=True)),
                ('precliente', models.ForeignKey(blank=True, to='cadastro.PreCliente', null=True)),
                ('responsavel_contato', models.ForeignKey(related_name=b'solicitacao_contato_set', blank=True, to='rh.Funcionario', null=True)),
                ('responsavel_correcao', models.ForeignKey(related_name=b'solicitacao_correcao_set', blank=True, to='rh.Funcionario', null=True)),
                ('responsavel_visto', models.ForeignKey(related_name=b'solicitacao_visto_set', blank=True, to='rh.Funcionario', null=True)),
            ],
            options={
                'ordering': ['prioridade', 'criado'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='solicitacao',
            name='tipo',
            field=models.ForeignKey(verbose_name=b'Tipo de Solicita\xc3\xa7\xc3\xa3o', to='solicitacao.TipoSolicitacao'),
            preserve_default=True,
        ),
    ]
