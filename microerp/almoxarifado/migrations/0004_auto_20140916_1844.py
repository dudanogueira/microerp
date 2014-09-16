# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import almoxarifado.models


class Migration(migrations.Migration):

    dependencies = [
        ('almoxarifado', '0003_auto_20140916_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controledeequipamento',
            name='arquivo_impresso_assinado',
            field=models.FileField(null=True, upload_to=almoxarifado.models.anexo_controle_de_equipamento_local, blank=True),
        ),
    ]
