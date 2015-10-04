# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0031_auto_20150907_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='chave_identificadora',
            field=models.CharField(default='padrao', max_length=30),
            preserve_default=False,
        ),
    ]
