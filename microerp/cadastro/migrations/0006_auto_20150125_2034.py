# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0005_cliente_id_referencia_criado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recado',
            name='adicionado_por',
        ),
        migrations.RemoveField(
            model_name='recado',
            name='cliente',
        ),
        migrations.RemoveField(
            model_name='recado',
            name='destinatario',
        ),
        migrations.RemoveField(
            model_name='recado',
            name='remetente',
        ),
        migrations.DeleteModel(
            name='Recado',
        ),
    ]
