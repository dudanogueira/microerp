# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0002_arquivoimportacaoprodutos'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='arquivoimportacaoprodutos',
            options={'ordering': ('criado',)},
        ),
    ]
