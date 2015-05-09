# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0019_contratofechado_conta_transferencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratofechado',
            name='foro',
            field=models.TextField(null=True, verbose_name=b'Foro', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='rescisao',
            field=models.TextField(null=True, verbose_name=b'Rescis\xc3\xa3o', blank=True),
            preserve_default=True,
        ),
    ]
