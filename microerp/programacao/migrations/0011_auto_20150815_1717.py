# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0010_auto_20150321_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followupdeordemdeservico',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='followupdeordemdeservico',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='ordemdeservico',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='ordemdeservico',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilacessoprogramacao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessoprogramacao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='tarefadeprogramacao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='tarefadeprogramacao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='tarefadeprogramacao',
            name='funcionarios_participantes',
            field=models.ManyToManyField(related_name='contratos_participantes_programacao', to='rh.Funcionario', blank=True),
        ),
    ]
