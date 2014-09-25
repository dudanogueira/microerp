# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0004_auto_20140925_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followupdepropostacomercial',
            name='visita',
            field=models.BooleanField(default=False, help_text='Indica se houve visita f\xedsica neste FollowUp', verbose_name='Registra Visita Comercial'),
        ),
    ]
