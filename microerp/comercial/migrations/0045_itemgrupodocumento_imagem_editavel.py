# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0044_itemgrupodocumento_texto_editavel'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='imagem_editavel',
            field=models.BooleanField(default=False),
        ),
    ]
