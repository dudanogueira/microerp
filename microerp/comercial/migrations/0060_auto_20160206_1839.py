# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-06 20:39
from __future__ import unicode_literals

import comercial.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0059_auto_20160131_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentogerado',
            name='capa',
            field=models.ImageField(blank=True, null=True, upload_to=comercial.models.CapaDocumentoDir()),
        ),
        migrations.AlterField(
            model_name='dadovariavel',
            name='chave',
            field=models.CharField(max_length=100),
        ),
    ]