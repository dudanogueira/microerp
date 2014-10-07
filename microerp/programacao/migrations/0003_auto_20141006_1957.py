# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0002_auto_20141006_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='data_fim',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 6, 19, 57, 4, 315809)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='data_inicio',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 6, 19, 57, 15, 326194)),
            preserve_default=False,
        ),
    ]
