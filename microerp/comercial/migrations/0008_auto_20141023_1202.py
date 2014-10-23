# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0007_auto_20141006_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratofechado',
            name='documento_proposto_legal',
            field=models.CharField(max_length=100, verbose_name=b'Documento Legal do Proposto (CPF)', blank=True),
        ),
    ]
