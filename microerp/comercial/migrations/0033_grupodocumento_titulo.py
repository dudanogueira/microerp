# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0032_itemgrupodocumento_chave_identificadora'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupodocumento',
            name='titulo',
            field=models.CharField(default='Titulo', max_length=150),
            preserve_default=False,
        ),
    ]
