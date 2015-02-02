# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0002_auto_20150126_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='canal',
            field=models.ForeignKey(verbose_name=b'Canal da Solicita\xc3\xa7\xc3\xa3o', to='solicitacao.CanalSolicitacao'),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime(2015, 2, 5, 19, 41, 59, 288248)),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='tipo',
            field=models.ForeignKey(verbose_name=b'Tipo de Solicita\xc3\xa7\xc3\xa3o', to='solicitacao.TipoSolicitacao'),
        ),
    ]
