# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacao', '0003_auto_20141006_1957'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarefadeprogramacao',
            name='cliente',
        ),
        migrations.AddField(
            model_name='tarefadeprogramacao',
            name='descricao',
            field=models.TextField(default='desc', blank=True),
            preserve_default=False,
        ),
    ]
