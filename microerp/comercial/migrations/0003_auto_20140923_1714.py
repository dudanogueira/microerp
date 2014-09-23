# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0002_auto_20140917_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orcamento',
            name='fim_promocao',
            field=models.DateField(null=True, verbose_name='Fim da Promo\xe7\xe3o', blank=True),
        ),
        migrations.AlterField(
            model_name='orcamento',
            name='inicio_promocao',
            field=models.DateField(null=True, verbose_name='In\xedcio da Promo\xe7\xe3o', blank=True),
        ),
    ]
