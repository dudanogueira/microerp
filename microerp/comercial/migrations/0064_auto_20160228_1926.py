# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-28 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0063_auto_20160209_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostacomercial',
            name='substitutivo',
            field=models.BooleanField(default=False, help_text=b'Define se Proposta possui or\xc3\xa7amentos substitutivos. Nessas propostas, o valor m\xc3\xadnimo n\xc3\xa3o \xc3\xa9 aplic\xc3\xa1vel.'),
        ),
        migrations.AlterField(
            model_name='dadovariavel',
            name='tipo',
            field=models.CharField(blank=True, choices=[(b'texto', b'Texto'), (b'inteiro', 'N\xfamero  Inteiro'), (b'decimal', 'N\xfamero Decimal')], default=b'texto ', max_length=100),
        ),
    ]
