# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0005_auto_20140925_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostacomercial',
            name='reaberta',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
