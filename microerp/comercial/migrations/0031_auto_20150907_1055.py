# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0030_auto_20150907_1046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentogerado',
            old_name='nome_modelo',
            new_name='nome',
        ),
    ]
