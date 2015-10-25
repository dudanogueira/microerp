# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0047_itemgrupodocumento_titulo_centralizado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemgrupodocumento',
            options={'ordering': ['peso']},
        ),
        migrations.AddField(
            model_name='documentogerado',
            name='imprime_logo',
            field=models.BooleanField(default=True),
        ),
    ]
