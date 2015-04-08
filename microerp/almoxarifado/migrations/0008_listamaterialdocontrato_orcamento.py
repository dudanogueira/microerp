# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0012_auto_20150208_1213'),
        ('almoxarifado', '0007_listamaterialdocontrato_ordem_de_servico'),
    ]

    operations = [
        migrations.AddField(
            model_name='listamaterialdocontrato',
            name='orcamento',
            field=models.OneToOneField(null=True, blank=True, to='comercial.Orcamento'),
            preserve_default=True,
        ),
    ]
