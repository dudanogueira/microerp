# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-06 22:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0060_auto_20160206_1839'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grupodadosvariaveis',
            name='contrato',
        ),
        migrations.RemoveField(
            model_name='grupodadosvariaveis',
            name='proposta',
        ),
        migrations.AddField(
            model_name='grupodadosvariaveis',
            name='documento',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comercial.DocumentoGerado'),
        ),
    ]