# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0004_auto_20140922_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='id_referencia_criado',
            field=models.BooleanField(default=False, help_text=b'Indica se o id de referencia foi criado pelo sistema'),
            preserve_default=True,
        ),
    ]
