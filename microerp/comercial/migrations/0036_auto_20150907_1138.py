# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0035_auto_20150907_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratofechado',
            name='documento_gerado',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='comercial.DocumentoGerado'),
        ),
    ]
