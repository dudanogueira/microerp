# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0008_auto_20141023_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostacomercial',
            name='tipos',
            field=models.ManyToManyField(related_name=b'proposta_por_tipos_set', null=True, to='comercial.TipoDeProposta', blank=True),
            preserve_default=True,
        ),
    ]
