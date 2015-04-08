# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0012_auto_20150208_1213'),
        ('almoxarifado', '0007_listamaterialdocontrato_ordem_de_servico'),
        ('programacao', '0007_auto_20150125_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarefadeprogramacao',
            name='contrato',
        ),
        migrations.AddField(
            model_name='ordemdeservico',
            name='contrato',
            field=models.ForeignKey(blank=True, to='comercial.ContratoFechado', help_text=b'Contrato Opcional', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='listas_material_exigido',
            field=models.ManyToManyField(to='almoxarifado.ListaMaterialDoContrato'),
            preserve_default=True,
        ),
    ]
