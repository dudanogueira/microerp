# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0041_itemgrupodocumento_quebra_pagina'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentogerado',
            name='versao',
            field=models.IntegerField(default=1),
        ),
    ]
