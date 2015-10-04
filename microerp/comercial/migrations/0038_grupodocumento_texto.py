# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0037_auto_20150907_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupodocumento',
            name='texto',
            field=models.TextField(null=True, blank=True),
        ),
    ]
