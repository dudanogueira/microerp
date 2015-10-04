# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0033_grupodocumento_titulo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupodocumento',
            name='titulo',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
    ]
