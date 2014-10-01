# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0003_auto_20141001_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivoimportacaoprodutos',
            name='importado_em',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 1, 9, 49, 43, 713793), blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='arquivoimportacaoprodutos',
            name='tipo',
            field=models.CharField(max_length=100, choices=[(b'digisat', b'Arquivo de Estoque do Digisat')]),
        ),
    ]
