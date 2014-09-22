# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0002_auto_20140917_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='ativo',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
