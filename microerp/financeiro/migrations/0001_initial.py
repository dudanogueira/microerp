# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comercial', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContaBancaria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LancamentoFinanceiroReceber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('peso', models.IntegerField(default=1)),
                ('situacao', models.CharField(default=b'a', max_length=1, choices=[(b'a', b'Aberto'), (b'r', b'Recebido'), (b'p', b'Pendente'), (b't', b'Antecipado')])),
                ('informacoes_pagamento', models.TextField(verbose_name='Informa\xe7\xf5es sobre o Pagamento', blank=True)),
                ('data_cobranca', models.DateField(default=datetime.datetime.today)),
                ('valor_cobrado', models.DecimalField(verbose_name=b'Valor Cobrado', max_digits=10, decimal_places=2)),
                ('valor_recebido', models.DecimalField(null=True, verbose_name=b'Valor Recebido', max_digits=10, decimal_places=2, blank=True)),
                ('modo_recebido', models.CharField(max_length=100, choices=[(b'boleto', b'Boleto'), (b'credito', 'Cart\xe3o de Cr\xe9dito'), (b'debito', 'Cart\xe3o de D\xe9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque'), (b'permuta', b'Permuta')])),
                ('data_recebido', models.DateField(null=True, blank=True)),
                ('data_recebido_em_conta', models.DateField(null=True, blank=True)),
                ('data_antecipado', models.DateField(null=True, verbose_name='Data da Antecipa\xe7\xe3o', blank=True)),
                ('antecipado', models.BooleanField(default=False)),
                ('valor_mao_de_obra', models.DecimalField(null=True, verbose_name=b'Valor da M\xc3\xa3o de Obra', max_digits=10, decimal_places=2, blank=True)),
                ('valor_materiais', models.DecimalField(null=True, verbose_name=b'Valor de Materiais', max_digits=10, decimal_places=2, blank=True)),
                ('notas_fiscais', models.TextField(blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('antecipado_por', models.ForeignKey(related_name=b'lancamento_antecipado_set', blank=True, to='rh.Funcionario', null=True)),
                ('conciliado_por', models.ForeignKey(related_name=b'lancamento_conciliado_set', blank=True, to='rh.Funcionario', null=True)),
                ('conta', models.ForeignKey(blank=True, to='financeiro.ContaBancaria', null=True)),
                ('contrato', models.ForeignKey(blank=True, to='comercial.ContratoFechado', null=True)),
                ('recebido_por', models.ForeignKey(related_name=b'lancamento_recebido_set', blank=True, to='rh.Funcionario', null=True)),
            ],
            options={
                'ordering': ('data_cobranca',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ObservacaoLancamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField(blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('criado_por', models.ForeignKey(related_name=b'observacaolancamento_criado_set', to='rh.Funcionario')),
                ('lancamento', models.ForeignKey(to='financeiro.LancamentoFinanceiroReceber')),
            ],
            options={
                'ordering': ('-criado',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAcessoFinanceiro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso ao Financeiro',
                'verbose_name_plural': 'Perfis de Acesso ao Financeiro',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessoAntecipacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor_inicial', models.DecimalField(verbose_name='Valor Inicial dos Lan\xe7amentos Antecipados', max_digits=10, decimal_places=2)),
                ('percentual_abatido', models.DecimalField(verbose_name='Percentual Abatido do Valor', max_digits=10, decimal_places=2)),
                ('valor_abatido', models.DecimalField(verbose_name='Valor Abatido dos Lan\xe7amentos Antecipados', max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('antecipado_por', models.ForeignKey(related_name=b'processoantecipacao_criado_set', to='rh.Funcionario')),
                ('lancamentos_receber', models.ManyToManyField(to='financeiro.LancamentoFinanceiroReceber')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='lancamentofinanceiroreceber',
            unique_together=set([('contrato', 'peso')]),
        ),
    ]
