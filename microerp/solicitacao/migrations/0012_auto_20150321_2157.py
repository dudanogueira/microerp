# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0011_auto_20150321_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime(2015, 3, 31, 21, 57, 22, 203712)),
        ),
    ]
