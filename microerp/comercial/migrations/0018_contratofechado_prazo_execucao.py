# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0017_contratofechado_endereco_obra'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='prazo_execucao',
            field=models.TextField(null=True, verbose_name=b'Prazos de Execu\xc3\xa7\xc3\xa3o', blank=True),
            preserve_default=True,
        ),
    ]
