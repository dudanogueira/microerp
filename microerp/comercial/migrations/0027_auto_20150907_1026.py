# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import comercial.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0026_auto_20150829_1911'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoGerado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('modelo', models.BooleanField(default=False)),
                ('tipo', models.CharField(max_length=15, choices=[(b'contrato', 'Contrato'), (b'orcamento', 'Or\xe7amento')])),
                ('nome_modelo', models.CharField(max_length=150, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GrupoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('peso', models.IntegerField()),
                ('documento', models.ForeignKey(to='comercial.DocumentoGerado')),
            ],
        ),
        migrations.CreateModel(
            name='ItemGrupoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('peso', models.IntegerField()),
                ('imagem', models.ImageField(upload_to=comercial.models.ImagemDocumentoDir())),
                ('grupo', models.ForeignKey(to='comercial.GrupoDocumento')),
            ],
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='descricao_items_proposto',
            field=models.TextField(verbose_name='Descri\xe7\xe3o dos Itens Proposto', blank=True),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='items_nao_incluso',
            field=models.TextField(verbose_name='Itens N\xe3o Incluso', blank=True),
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='documento_gerado',
            field=models.OneToOneField(null=True, blank=True, to='comercial.DocumentoGerado'),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='documento_gerado',
            field=models.OneToOneField(null=True, blank=True, to='comercial.DocumentoGerado'),
        ),
        migrations.AlterUniqueTogether(
            name='itemgrupodocumento',
            unique_together=set([('peso', 'grupo')]),
        ),
        migrations.AlterUniqueTogether(
            name='grupodocumento',
            unique_together=set([('peso', 'documento')]),
        ),
    ]
