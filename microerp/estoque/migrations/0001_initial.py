# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CodigoDeBarra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo_barras', models.CharField(max_length=100, blank=True)),
                ('padrao_codigo_de_barras', models.CharField(blank=True, max_length=100, choices=[(b'ean13', b'EAN13 - European Article Number'), (b'o', b'Outros')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAcessoEstoque',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso ao Estoque',
                'verbose_name_plural': 'Perfis de Acesso ao Estoque',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=500)),
                ('nome', models.CharField(max_length=300)),
                ('descricao', models.CharField(max_length=300)),
                ('ativo', models.BooleanField(default=True)),
                ('unidade_de_venda', models.CharField(default=b'un', max_length=100, null=True, blank=True, choices=[(b'un', b'Unidade'), (b'pc', b'Pe\xc3\xa7a'), (b'am', b'AM'), (b'pct', b'Pacote'), (b'bl', b'Bloco')])),
                ('unidade_de_compra', models.CharField(default=b'un', max_length=100, null=True, blank=True, choices=[(b'un', b'Unidade'), (b'pc', b'Pe\xc3\xa7a'), (b'am', b'AM'), (b'pct', b'Pacote'), (b'bl', b'Bloco')])),
                ('fator', models.CharField(max_length=100, null=True, blank=True)),
                ('quantidade_em_estoque', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('preco_custo', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('preco_venda', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('preco_consumo', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('ncm', models.IntegerField(null=True, blank=True)),
                ('tributacao', models.CharField(blank=True, max_length=100, choices=[(b'i', b'Isento'), (b's', b'Substitui\xc3\xa7\xc3\xa3o Tribut\xc3\xa1ria'), (b'n', b'Normal')])),
                ('substituicao_tributaria_valor', models.IntegerField(default=0)),
                ('icms', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Cria\xc3\xa7\xc3\xa3o', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualiza\xc3\xa7\xc3\xa3o', auto_now=True)),
                ('grupo_indicador', models.ForeignKey(blank=True, to='comercial.GrupoIndicadorDeProdutoProposto', null=True)),
                ('sub_grupo_indicador', models.ManyToManyField(to='comercial.SubGrupoIndicadorDeProdutoProposto', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TabelaDePreco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('percentual', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Cria\xc3\xa7\xc3\xa3o', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualiza\xc3\xa7\xc3\xa3o', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoDeProduto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Cria\xc3\xa7\xc3\xa3o', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualiza\xc3\xa7\xc3\xa3o', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='produto',
            name='tabela',
            field=models.ForeignKey(blank=True, to='estoque.TabelaDePreco', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='produto',
            name='tipo',
            field=models.ForeignKey(blank=True, to='estoque.TipoDeProduto', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='codigodebarra',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
    ]
