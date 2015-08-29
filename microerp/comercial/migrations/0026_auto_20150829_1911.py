# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0005_auto_20150815_1717'),
        ('comercial', '0025_empresacomercial_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='contas_disponiveis',
            field=models.ManyToManyField(to='financeiro.ContaBancaria', blank=True),
        ),
        migrations.AlterField(
            model_name='contratofechado',
            name='status',
            field=models.CharField(default=b'emaberto', max_length=100, verbose_name='Status/Situa\xe7\xe3o do Contrato', choices=[(b'cancelado', b'Cancelado'), (b'arquivado', b'Arquivado'), (b'emanalise', b'Em An\xc3\xa1lise'), (b'invalido', 'Inv\xe1lido'), (b'assinatura', 'Aguardando Assinatura'), (b'emaberto', b'Em Aberto'), (b'lancado', 'Contrato Lan\xe7ado')]),
        ),
        migrations.AlterField(
            model_name='perfilacessocomercial',
            name='super_gerente',
            field=models.BooleanField(default=False, verbose_name=b'Super Gerente'),
        ),
    ]
