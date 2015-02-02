# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0005_cliente_id_referencia_criado'),
        ('programacao', '0005_auto_20141221_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='cliente',
            field=models.ForeignKey(blank=True, to='cadastro.Cliente', null=True),
            preserve_default=True,
        ),
    ]
