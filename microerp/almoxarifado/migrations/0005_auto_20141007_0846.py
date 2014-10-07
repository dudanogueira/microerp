# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almoxarifado', '0004_auto_20141006_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linhalistamaterial',
            name='quantidade_ja_atendida',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='linhalistamaterial',
            name='quantidade_requisitada',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
