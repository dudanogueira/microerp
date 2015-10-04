# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0042_documentogerado_versao'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentogerado',
            name='empresa_vinculada',
            field=models.ManyToManyField(to='comercial.EmpresaComercial', blank=True),
        ),
    ]
