# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0052_auto_20151118_1322'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemgrupodocumento',
            options={'ordering': ['peso', 'chave_identificadora']},
        ),
        migrations.AlterUniqueTogether(
            name='itemgrupodocumento',
            unique_together=set([]),
        ),
    ]
