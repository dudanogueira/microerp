# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0024_empresacomercial_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
