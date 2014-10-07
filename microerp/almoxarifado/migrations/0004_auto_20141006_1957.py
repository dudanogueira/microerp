# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('estoque', '0005_auto_20141001_0953'),
        ('comercial', '0007_auto_20141006_1852'),
        ('almoxarifado', '0003_auto_20140917_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinhaListaMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade_requisitada', models.DecimalField(max_digits=10, decimal_places=2)),
                ('quantidade_ja_atendida', models.DecimalField(max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaListaMaterialCompra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.DecimalField(max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaListaMaterialEntregue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.DecimalField(max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ListaMaterialCompra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ativa', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('contrato', models.ForeignKey(blank=True, to='comercial.ContratoFechado', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ListaMaterialDoContrato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ativa', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('contrato', models.OneToOneField(null=True, blank=True, to='comercial.ContratoFechado')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ListaMaterialEntregue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entregue', models.BooleanField(default=False)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('contrato', models.ForeignKey(blank=True, to='comercial.ContratoFechado', null=True)),
                ('entregue_para', models.ForeignKey(related_name=b'entregue_para_set', to='rh.Funcionario')),
                ('entregue_por', models.ForeignKey(related_name=b'entregue_por_set', to='rh.Funcionario')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='linhalistamaterialentregue',
            name='lista',
            field=models.ForeignKey(to='almoxarifado.ListaMaterialEntregue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linhalistamaterialentregue',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linhalistamaterialcompra',
            name='lista',
            field=models.ForeignKey(to='almoxarifado.ListaMaterialCompra'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linhalistamaterialcompra',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linhalistamaterial',
            name='lista',
            field=models.ForeignKey(to='almoxarifado.ListaMaterialDoContrato'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linhalistamaterial',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
    ]
