# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('almoxarifado', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linhacontroleequipamento',
            name='funcionario_receptor',
            field=models.ForeignKey(related_name=b'recepcao_linha_controle_equipamento_set', blank=True, to='rh.Funcionario', help_text=b'Funcion\xc3\xa1rio respons\xc3\xa1vel pela entrega do equipamento.', null=True, verbose_name='Funcion\xe1rio que Autorizou o Controle'),
            preserve_default=True,
        ),
    ]
