# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0012_auto_20150208_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostacomercial',
            name='estado_do_proposto',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
