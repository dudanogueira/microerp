# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0016_contratofechado_normas_execucao'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='endereco_obra',
            field=models.TextField(null=True, verbose_name='Endere\xe7o da Obra', blank=True),
            preserve_default=True,
        ),
    ]
