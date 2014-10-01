# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0004_auto_20141001_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arquivoimportacaoprodutos',
            name='importado_em',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
