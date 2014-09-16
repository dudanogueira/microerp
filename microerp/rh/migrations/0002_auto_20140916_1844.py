# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaodelicenca',
            name='fim',
            field=models.DateField(default=datetime.datetime(2014, 9, 20, 18, 44, 51, 516053), verbose_name='T\xe9rmino da Licen\xe7a'),
        ),
    ]
