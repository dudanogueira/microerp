# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0018_auto_20150509_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilacessosolicitacao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessosolicitacao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='departamentos_afetados',
            field=models.ManyToManyField(related_name='solicitacao_afetada_set', to='rh.Departamento', blank=True),
        ),
    ]
