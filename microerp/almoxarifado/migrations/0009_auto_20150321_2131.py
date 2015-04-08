# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0010_auto_20150321_2131'),
        ('almoxarifado', '0008_listamaterialdocontrato_orcamento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listamaterialcompra',
            name='contrato',
        ),
        migrations.RemoveField(
            model_name='listamaterialentregue',
            name='contrato',
        ),
        migrations.AddField(
            model_name='listamaterialcompra',
            name='ordem_de_servico',
            field=models.ForeignKey(blank=True, to='programacao.OrdemDeServico', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listamaterialentregue',
            name='ordem_de_servico',
            field=models.ForeignKey(blank=True, to='programacao.OrdemDeServico', null=True),
            preserve_default=True,
        ),
    ]
