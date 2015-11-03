# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0048_auto_20151025_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='responsavel_legal',
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
    ]
