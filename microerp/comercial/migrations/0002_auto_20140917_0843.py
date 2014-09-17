# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('comercial', '0001_initial'),
        ('cadastro', '0002_auto_20140917_0843'),
        ('estoque', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linharecursomaterial',
            name='produto',
            field=models.ForeignKey(to='estoque.Produto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linharecursologistico',
            name='proposta',
            field=models.ForeignKey(to='comercial.PropostaComercial'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linharecursologistico',
            name='tipo',
            field=models.ForeignKey(to='comercial.TipoRecursoLogistico'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linharecursohumano',
            name='cargo',
            field=models.ForeignKey(to='rh.Cargo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linharecursohumano',
            name='orcamento',
            field=models.ForeignKey(to='comercial.Orcamento'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lancamentodefechamentocomissao',
            name='fechamento',
            field=models.ForeignKey(to='comercial.FechamentoDeComissao'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='followupdepropostacomercial',
            name='criado_por',
            field=models.ForeignKey(related_name=b'followup_adicionado_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='followupdepropostacomercial',
            name='proposta',
            field=models.ForeignKey(to='comercial.PropostaComercial'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fechamentodecomissao',
            name='comissionado',
            field=models.ForeignKey(related_name=b'fechamento_comissao__set', verbose_name='Respons\xe1vel Comissionado', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fechamentodecomissao',
            name='contratos',
            field=models.ManyToManyField(to='comercial.ContratoFechado'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fechamentodecomissao',
            name='criado_por',
            field=models.ForeignKey(related_name=b'fechamento_comissao_criado_set', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='apoio_tecnico',
            field=models.ForeignKey(related_name=b'contratos_apoio_tecnico', verbose_name='Apoio T\xe9cnico', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='categoria',
            field=models.ForeignKey(blank=True, to='comercial.CategoriaContratoFechado', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='cliente',
            field=models.ForeignKey(to='cadastro.Cliente'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='funcionario_validador',
            field=models.ForeignKey(related_name=b'contrato_validado_set', verbose_name='Funcion\xe1rio que Validou', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='funcionarios_participantes',
            field=models.ManyToManyField(related_name=b'contratos_participados', null=True, to='rh.Funcionario', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='responsavel',
            field=models.ForeignKey(verbose_name='Respons\xe1vel pelo Contrato', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contratofechado',
            name='responsavel_comissionado',
            field=models.ForeignKey(related_name=b'contrato_comissionado_set', verbose_name='Respons\xe1vel Comissionado', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
    ]
