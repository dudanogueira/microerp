# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0006_propostacomercial_reaberta'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='linharecursomaterial',
            options={'ordering': ('produto__codigo',)},
        ),
    ]
