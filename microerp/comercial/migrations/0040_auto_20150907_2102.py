# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0039_grupodocumento_chave_identificadora'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grupodocumento',
            name='chave_identificadora',
        ),
        migrations.RemoveField(
            model_name='grupodocumento',
            name='texto',
        ),
        migrations.RemoveField(
            model_name='grupodocumento',
            name='titulo',
        ),
    ]
