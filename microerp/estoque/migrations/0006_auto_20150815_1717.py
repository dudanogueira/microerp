# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0005_auto_20141001_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arquivoimportacaoprodutos',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='arquivoimportacaoprodutos',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilacessoestoque',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessoestoque',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='sub_grupo_indicador',
            field=models.ManyToManyField(to='comercial.SubGrupoIndicadorDeProdutoProposto', blank=True),
        ),
        migrations.AlterField(
            model_name='tabeladepreco',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='tabeladepreco',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='tipodeproduto',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='tipodeproduto',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
    ]
