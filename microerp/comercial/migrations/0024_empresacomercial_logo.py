# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import comercial.models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0023_auto_20150816_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='logo',
            field=models.ImageField(null=True, upload_to=comercial.models.LogoEmpresaDir(), blank=True),
        ),
    ]
