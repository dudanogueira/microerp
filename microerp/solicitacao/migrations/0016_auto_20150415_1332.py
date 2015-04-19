# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0015_auto_20150415_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime(2015, 4, 25, 13, 31, 51, 85387)),
        ),
    ]
