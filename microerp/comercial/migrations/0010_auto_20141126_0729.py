# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0009_propostacomercial_tipos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupoindicadordeprodutoproposto',
            name='nome',
            field=models.CharField(max_length=100),
        ),
    ]
