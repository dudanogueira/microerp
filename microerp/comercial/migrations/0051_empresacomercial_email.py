# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0050_auto_20151030_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
