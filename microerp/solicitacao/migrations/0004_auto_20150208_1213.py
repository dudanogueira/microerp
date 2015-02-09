# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0003_auto_20150126_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime(2015, 2, 18, 12, 13, 29, 810596)),
        ),
    ]
