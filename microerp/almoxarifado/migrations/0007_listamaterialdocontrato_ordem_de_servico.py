# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0007_auto_20150125_2034'),
        ('almoxarifado', '0006_auto_20141007_0848'),
    ]

    operations = [
        migrations.AddField(
            model_name='listamaterialdocontrato',
            name='ordem_de_servico',
            field=models.OneToOneField(null=True, blank=True, to='programacao.OrdemDeServico'),
            preserve_default=True,
        ),
    ]
