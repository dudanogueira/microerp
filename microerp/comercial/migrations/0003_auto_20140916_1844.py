# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0002_auto_20140916_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followupdepropostacomercial',
            name='data_expiracao',
            field=models.DateField(default=datetime.datetime(2014, 9, 23, 18, 44, 51, 571555), verbose_name=b'Data de Expira\xc3\xa7\xc3\xa3o'),
        ),
    ]
