# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0046_auto_20151004_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='titulo_centralizado',
            field=models.BooleanField(default=False),
        ),
    ]
