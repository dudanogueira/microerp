# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0004_auto_20150509_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lancamentofinanceiroreceber',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='lancamentofinanceiroreceber',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='observacaolancamento',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='observacaolancamento',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilacessofinanceiro',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessofinanceiro',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='processoantecipacao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='processoantecipacao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
    ]
