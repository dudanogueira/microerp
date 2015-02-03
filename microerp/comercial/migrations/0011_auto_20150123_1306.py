# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0010_auto_20141126_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratofechado',
            name='status_execucao',
            field=models.CharField(default=b'naoiniciado', max_length=100, verbose_name='Status da Execu\xe7\xe3o do Contrato', choices=[(b'naoiniciado', b'N\xc3\xa3o Iniciado'), (b'comunicadoinicio', b'In\xc3\xadcio do Contrato Comunicado'), (b'emandamento', b'Em Andamento'), (b'pendente', b'Pendente'), (b'finalizado', b'Finalizado'), (b'comunicadofim', b'Fim do Contrato Comunicado')]),
        ),
    ]
