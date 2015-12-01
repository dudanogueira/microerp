# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0028_auto_20150907_1030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentogerado',
            name='tipo',
        ),
        migrations.AddField(
            model_name='documentogerado',
            name='tipo',
            field=models.ForeignKey(blank=True, to='comercial.TipoDeProposta', null=True),
        )
    ]
