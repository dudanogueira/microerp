# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0020_auto_20150509_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratofechado',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='contratofechado',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='contratofechado',
            name='funcionarios_participantes',
            field=models.ManyToManyField(related_name='contratos_participados', to='rh.Funcionario', blank=True),
        ),
        migrations.AlterField(
            model_name='fechamentodecomissao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='fechamentodecomissao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='followupdepropostacomercial',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='followupdepropostacomercial',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='linharecursohumano',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='linharecursohumano',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='linharecursologistico',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='linharecursologistico',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='linharecursomaterial',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='linharecursomaterial',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='orcamento',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='orcamento',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilacessocomercial',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessocomercial',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='parcelamentos_possiveis',
            field=models.ManyToManyField(to='comercial.TabelaDeParcelamento', verbose_name='Parcelamenos Poss\xedveis', blank=True),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='tipos',
            field=models.ManyToManyField(related_name='proposta_por_tipos_set', to='comercial.TipoDeProposta', blank=True),
        ),
        migrations.AlterField(
            model_name='requisicaodeproposta',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='requisicaodeproposta',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='tipodecontratofechado',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='tipodecontratofechado',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
    ]
