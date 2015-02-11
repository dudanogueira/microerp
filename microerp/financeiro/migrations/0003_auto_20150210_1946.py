# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0002_auto_20150208_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lancamentofinanceiroreceber',
            name='observacao_recebido',
            field=models.TextField(null=True, verbose_name='Observa\xe7\xf5es', blank=True),
        ),
    ]
