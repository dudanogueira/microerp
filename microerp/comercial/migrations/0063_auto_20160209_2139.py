# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-09 23:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0062_dadovariavel_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadovariavel',
            name='valor',
            field=models.TextField(blank=True, null=True),
        ),
    ]
