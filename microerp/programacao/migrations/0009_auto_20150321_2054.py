# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('programacao', '0008_auto_20150321_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowUpDeOrdemDeServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField()),
                ('porcentagem_execucao', models.DecimalField(max_digits=3, decimal_places=0)),
                ('tipo', models.CharField(blank=True, max_length=100, choices=[(b'informacao', 'Informa\xe7\xe3o'), (b'inicio_comunicado', 'In\xedcio Comunicado'), (b'emandamento', 'Em Andamento'), (b'pendente', 'Pendente'), (b'clientependente', 'Cliente Pendente'), (b'finalizado', 'Finalizado')])),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('criado_por', models.ForeignKey(related_name=b'followup_contrato_adicionado_set', to='rh.Funcionario')),
                ('ordem_de_servico', models.ForeignKey(to='programacao.OrdemDeServico')),
            ],
            options={
                'ordering': ['-criado'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='followupdecontrato',
            name='contrato',
        ),
        migrations.RemoveField(
            model_name='followupdecontrato',
            name='criado_por',
        ),
        migrations.DeleteModel(
            name='FollowUpDeContrato',
        ),
    ]
