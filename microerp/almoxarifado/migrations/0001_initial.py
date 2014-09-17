# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import almoxarifado.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ControleDeEquipamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'pendente', max_length=100, choices=[(b'pendente', b'Controle Pendente'), (b'fechado', b'Controle Fechado')])),
                ('observacao', models.TextField(verbose_name='Observa\xe7\xe3o', blank=True)),
                ('tipo', models.CharField(blank=True, max_length=100, choices=[(b'epi', b'Controle de EPI'), (b'ferramenta', b'Controle de Ferramentas')])),
                ('arquivo_impresso_assinado', models.FileField(null=True, upload_to=almoxarifado.models.AnexoControleDir(), blank=True)),
                ('data_arquivo_impresso_assinado_recebido', models.DateField(default=datetime.datetime.today)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'verbose_name': 'Controle de Equipamento',
                'verbose_name_plural': 'Controles de Equipamento',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaControleEquipamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unidade', models.CharField(max_length=10, blank=True)),
                ('quantidade', models.DecimalField(max_digits=10, decimal_places=2)),
                ('data_entregue', models.DateField(null=True, blank=True)),
                ('codigo_ca', models.CharField(max_length=100, null=True, verbose_name=b'C\xc3\xb3digo CA', blank=True)),
                ('data_previsao_devolucao', models.DateField()),
                ('data_devolvido', models.DateField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('controle', models.ForeignKey(to='almoxarifado.ControleDeEquipamento')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
