# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0022_auto_20150816_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilacessocomercial',
            name='super_gerente',
            field=models.BooleanField(default=False, verbose_name=b'Gerente das Empresas'),
        ),
        migrations.AlterField(
            model_name='perfilacessocomercial',
            name='gerente',
            field=models.BooleanField(default=False, verbose_name=b'Gerente da Empresa'),
        ),
    ]
