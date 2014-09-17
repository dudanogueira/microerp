# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('almoxarifado', '0002_linhacontroleequipamento_funcionario_receptor'),
        ('estoque', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linhacontroleequipamento',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='controledeequipamento',
            name='criado_por',
            field=models.ForeignKey(related_name=b'controledeequipamento_criado_set', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='controledeequipamento',
            name='funcionario',
            field=models.ForeignKey(verbose_name=b'Funcion\xc3\xa1rio Solicitante', to='rh.Funcionario', help_text=b'Funcion\xc3\xa1rio respons\xc3\xa1vel pela retirada do equipamento.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='controledeequipamento',
            name='receptor_arquivo_impresso',
            field=models.ForeignKey(related_name=b'autorizacao_controle_equipamento_set', blank=True, to='rh.Funcionario', help_text=b'Funcion\xc3\xa1rio respons\xc3\xa1vel pela entrega do equipamento.', null=True, verbose_name='Funcion\xe1rio que Autorizou o Controle'),
            preserve_default=True,
        ),
    ]
