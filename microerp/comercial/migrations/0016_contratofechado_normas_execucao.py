# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0015_auto_20150415_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='normas_execucao',
            field=models.TextField(null=True, verbose_name=b'Normas de Execu\xc3\xa7\xc3\xa3o', blank=True),
            preserve_default=True,
        ),
    ]
