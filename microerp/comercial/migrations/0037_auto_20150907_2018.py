# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0036_auto_20150907_1138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grupodocumento',
            options={'ordering': ['peso']},
        ),
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='texto',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='titulo',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
    ]
