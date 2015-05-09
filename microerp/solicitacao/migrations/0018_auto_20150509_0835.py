# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0017_auto_20150415_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]
