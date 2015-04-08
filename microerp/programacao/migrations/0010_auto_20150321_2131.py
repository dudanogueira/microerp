# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0009_auto_20150321_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdeservico',
            name='data_fim',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ordemdeservico',
            name='data_inicio',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
