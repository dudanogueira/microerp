# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0004_auto_20141221_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='titulo',
            field=models.CharField(default='Titulo', max_length=100, verbose_name='T\xedtulo', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tarefadeprogramacao',
            name='descricao',
            field=models.TextField(verbose_name='Descri\xe7\xe3o da Atividade', blank=True),
        ),
    ]
