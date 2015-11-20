# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0054_tipodeproposta_tipo_contrato_mapeado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipodeproposta',
            name='tipo_contrato_mapeado',
            field=models.ForeignKey(blank=True, to='comercial.CategoriaContratoFechado', null=True),
        ),
    ]
