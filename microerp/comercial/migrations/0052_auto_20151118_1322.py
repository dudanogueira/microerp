# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0051_empresacomercial_email'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='grupodocumento',
            unique_together=set([]),
        ),
    ]
