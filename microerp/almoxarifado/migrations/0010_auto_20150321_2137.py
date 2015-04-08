# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almoxarifado', '0009_auto_20150321_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listamaterialdocontrato',
            name='ordem_de_servico',
            field=models.ForeignKey(blank=True, to='programacao.OrdemDeServico', null=True),
        ),
    ]
