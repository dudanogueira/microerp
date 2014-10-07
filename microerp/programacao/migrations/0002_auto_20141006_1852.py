# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tarefadeprogramacao',
            options={'ordering': ('criado',)},
        ),
        migrations.AlterField(
            model_name='followupdecontrato',
            name='contrato',
            field=models.ForeignKey(to='comercial.ContratoFechado'),
        ),
    ]
