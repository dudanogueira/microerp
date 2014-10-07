# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('almoxarifado', '0005_auto_20141007_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linhalistamaterial',
            name='produto',
            field=models.ForeignKey(blank=True, to='estoque.Produto', null=True),
        ),
    ]
