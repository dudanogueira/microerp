# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0029_auto_20150907_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentogerado',
            name='tipo_proposta',
            field=models.ForeignKey(blank=True, to='comercial.TipoDeProposta', null=True),
        ),
        migrations.AlterField(
            model_name='documentogerado',
            name='tipo',
            field=models.CharField(default=b'proposta', max_length=15, choices=[(b'contrato', 'Contrato'), (b'proposta', 'Proposta')]),
        ),
    ]
