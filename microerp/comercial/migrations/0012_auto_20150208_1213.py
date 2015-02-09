# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0011_auto_20150123_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratofechado',
            name='forma_pagamento',
            field=models.CharField(default=b'dinheiro', max_length=100, verbose_name=b'Forma de Pagamento', choices=[(b'boleto', b'Boleto'), (b'credito', 'Cart\xe3o de Cr\xe9dito'), (b'debito', 'Cart\xe3o de D\xe9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque'), (b'transferencia', 'Transfer\xeancia Banc\xe1ria'), (b'permuta', b'Permuta')]),
        ),
    ]
