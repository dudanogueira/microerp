# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0004_auto_20150509_0835'),
        ('comercial', '0018_contratofechado_prazo_execucao'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='conta_transferencia',
            field=models.ForeignKey(blank=True, to='financeiro.ContaBancaria', null=True),
            preserve_default=True,
        ),
    ]
