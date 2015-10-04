# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0040_auto_20150907_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='quebra_pagina',
            field=models.BooleanField(default=False),
        ),
    ]
