# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0038_grupodocumento_texto'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupodocumento',
            name='chave_identificadora',
            field=models.CharField(default='padrao', max_length=30),
            preserve_default=False,
        ),
    ]
