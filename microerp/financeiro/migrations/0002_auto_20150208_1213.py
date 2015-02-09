# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lancamentofinanceiroreceber',
            name='observacao_recebido',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lancamentofinanceiroreceber',
            name='modo_recebido',
            field=models.CharField(max_length=100, choices=[(b'boleto', b'Boleto'), (b'credito', 'Cart\xe3o de Cr\xe9dito'), (b'debito', 'Cart\xe3o de D\xe9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque'), (b'transferencia', 'Transfer\xeancia Banc\xe1ria'), (b'permuta', b'Permuta')]),
        ),
    ]
