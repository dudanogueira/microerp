# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0043_documentogerado_empresa_vinculada'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='texto_editavel',
            field=models.BooleanField(default=False),
        ),
    ]
