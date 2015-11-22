# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0054_itemgrupodocumento_possui_variavel'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='data_assinatura',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='itemgrupodocumento',
            name='possui_variavel',
            field=models.BooleanField(default=False, help_text='Este item possui valores que precisam ser alterados.'),
        ),
    ]
