# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import estoque.models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('estoque', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArquivoImportacaoProdutos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('importado', models.BooleanField(default=False)),
                ('tipo', models.CharField(blank=True, max_length=100, choices=[(b'digisat', b'Arquivo de Estoque do Digisat')])),
                ('arquivo', models.FileField(upload_to=estoque.models.ArquivoImportacaoDir())),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Cria\xc3\xa7\xc3\xa3o', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualiza\xc3\xa7\xc3\xa3o', auto_now=True)),
                ('enviado_por', models.ForeignKey(to='rh.Funcionario')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
