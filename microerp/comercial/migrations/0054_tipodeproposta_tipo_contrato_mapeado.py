# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0053_auto_20151118_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipodeproposta',
            name='tipo_contrato_mapeado',
            field=models.ForeignKey(blank=True, to='comercial.TipodeContratoFechado', null=True),
        ),
    ]
