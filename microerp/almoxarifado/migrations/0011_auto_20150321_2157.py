# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almoxarifado', '0010_auto_20150321_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linhalistamaterial',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
        ),
    ]
