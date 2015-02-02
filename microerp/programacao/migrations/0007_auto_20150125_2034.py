# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0006_auto_20150125_2034'),
        ('programacao', '0006_tarefadeprogramacao_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdemDeServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'naoiniciado', max_length=100, blank=True, choices=[(b'naoiniciado', b'N\xc3\xa3o Iniciado'), (b'comunicadoinicio', b'In\xc3\xadcio da Ordem de Servi\xc3\xa7o Comunicado'), (b'emandamento', b'Em Andamento'), (b'atrazado', b'Atrazado'), (b'pendente', b'Pendente'), (b'finalizado', b'Finalizado'), (b'comunicadofim', b'Fim da Ordem de Servi\xc3\xa7o Comunicado')])),
                ('valor', models.DecimalField(max_digits=10, decimal_places=2)),
                ('data_inicio', models.DateTimeField()),
                ('data_fim', models.DateTimeField()),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('cliente', models.ForeignKey(to='cadastro.Cliente')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='tarefadeprogramacao',
            name='cliente',
        ),
        migrations.AddField(
            model_name='followupdecontrato',
            name='tipo',
            field=models.CharField(default=1, max_length=100, blank=True, choices=[(b'informacao', 'Informa\xe7\xe3o'), (b'inicio_comunicado', 'In\xedcio Comunicado'), (b'emandamento', 'Em Andamento'), (b'pendente', 'Pendente'), (b'clientependente', 'Cliente Pendente'), (b'finalizado', 'Finalizado')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='ordem_de_servico',
            field=models.ForeignKey(blank=True, to='programacao.OrdemDeServico', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarefadeprogramacao',
            name='status_execucao',
            field=models.CharField(default=b'naoiniciado', max_length=100, verbose_name='Status da Execu\xe7\xe3o da Tarefa de Programa\xe7\xe3o', choices=[(b'naoiniciado', 'N\xe3o Iniciado'), (b'emandamento', 'Em Andamento'), (b'pendente', 'Pendente'), (b'clientependente', 'Cliente Pendente'), (b'atrasado', 'Atrasado'), (b'finalizado', 'Finalizado')]),
        ),
    ]
