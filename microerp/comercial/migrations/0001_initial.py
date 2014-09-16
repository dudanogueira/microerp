# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import comercial.models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastro', '0002_auto_20140916_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaContratoFechado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContratoFechado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('objeto', models.TextField()),
                ('nome_proposto_legal', models.CharField(max_length=100, blank=True)),
                ('documento_proposto_legal', models.CharField(max_length=100, blank=True)),
                ('garantia', models.TextField(blank=True)),
                ('items_incluso', models.TextField(verbose_name=b'Itens Incluso', blank=True)),
                ('items_nao_incluso', models.TextField(verbose_name=b'Itens N\xc3\xa3o Incluso', blank=True)),
                ('forma_pagamento', models.CharField(default=b'dinheiro', max_length=100, verbose_name=b'Forma de Pagamento', choices=[(b'boleto', b'Boleto'), (b'credito', 'Cart\xe3o de Cr\xe9dito'), (b'debito', 'Cart\xe3o de D\xe9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque'), (b'permuta', b'Permuta')])),
                ('parcelas', models.IntegerField(default=1, verbose_name=b'Quantidade de Parcelas')),
                ('inicio_cobranca', models.DateField(default=datetime.datetime.today, verbose_name='In\xedcio da Cobran\xe7a')),
                ('valor', models.DecimalField(verbose_name=b'Valor do Contrato', max_digits=10, decimal_places=2)),
                ('valor_entrada', models.DecimalField(default=0, verbose_name=b'Valor de Entrada', max_digits=10, decimal_places=2)),
                ('receber_apos_conclusao', models.BooleanField(default=False, verbose_name=b'Receber ap\xc3\xb3s a conclus\xc3\xa3o do Contrato')),
                ('tipo', models.CharField(default=b'fechado', max_length=100, choices=[(b'aberto', b'Aberto'), (b'fechado', b'Fechado'), (b'mensal', b'Mensal')])),
                ('status', models.CharField(default=b'emaberto', max_length=100, verbose_name='Status/Situa\xe7\xe3o do Contrato', choices=[(b'cancelado', b'Cancelado'), (b'emanalise', b'Em An\xc3\xa1lise'), (b'invalido', 'Inv\xe1lido'), (b'assinatura', 'Aguardando Assinatura'), (b'emaberto', b'Em Aberto'), (b'lancado', 'Contrato Lan\xe7ado')])),
                ('status_execucao', models.CharField(default=b'naoiniciado', max_length=100, verbose_name='Status da Execu\xe7\xe3o do Contrato', choices=[(b'naoiniciado', b'N\xc3\xa3o Iniciado'), (b'emandamento', b'Em Andamento'), (b'pendente', b'Pendente'), (b'finalizado', b'Finalizado')])),
                ('porcentagem_execucao', models.DecimalField(default=0, max_digits=3, decimal_places=0)),
                ('termo_de_entrega_recebido', models.BooleanField(default=False)),
                ('numero_termo_de_entrega', models.CharField(max_length=100, blank=True)),
                ('aguardando_cliente', models.BooleanField(default=False)),
                ('data_aguardando_cliente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_emandamento', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_pendente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_retorno_cliente', models.DateTimeField(null=True, blank=True)),
                ('data_marcado_finalizado', models.DateTimeField(null=True, blank=True)),
                ('previsao_inicio_execucao', models.DateField(default=datetime.datetime.today)),
                ('previsao_termino_execucao', models.DateField(null=True, blank=True)),
                ('efetivo_inicio_execucao', models.DateField(default=datetime.datetime.today)),
                ('efetivo_termino_execucao', models.DateField(null=True, blank=True)),
                ('concluido', models.BooleanField(default=False)),
                ('motivo_invalido', models.TextField(blank=True)),
                ('observacoes', models.TextField(blank=True)),
                ('data_validacao', models.DateTimeField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FechamentoDeComissao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FollowUpDePropostaComercial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField()),
                ('reagenda_data_expiracao', models.BooleanField(default=False, verbose_name=b'Reagenda Nova Data de Expira\xc3\xa7\xc3\xa3o')),
                ('data_expiracao', models.DateField(default=datetime.datetime(2014, 9, 23, 9, 27, 27, 101673), verbose_name=b'Data de Expira\xc3\xa7\xc3\xa3o')),
                ('probabilidade', models.IntegerField(null=True, verbose_name=b'Probabilidade (%)', blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'ordering': ['-criado'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GrupoIndicadorDeProdutoProposto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LancamentoDeFechamentoComissao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(max_digits=10, decimal_places=2)),
                ('pago', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaRecursoHumano',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custo_unitario', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('custo_total', models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)),
                ('quantidade', models.IntegerField(verbose_name=b'Quantidade de Horas')),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaRecursoLogistico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custo_total', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('descricao', models.TextField(blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinhaRecursoMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custo_unitario', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('custo_total', models.DecimalField(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
                ('quantidade', models.DecimalField(max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Orcamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=100, verbose_name='Descri\xe7\xe3o', blank=True)),
                ('selecionado', models.BooleanField(default=True)),
                ('modelo', models.BooleanField(default=False)),
                ('tabelado', models.BooleanField(default=False)),
                ('promocao', models.BooleanField(default=False)),
                ('inicio_promocao', models.DateField(null=True, blank=True)),
                ('fim_promocao', models.DateField(null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('custo_total', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('custo_material', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('custo_humano', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('criado_por', models.ForeignKey(related_name=b'orcamento_criado_set', blank=True, to='rh.Funcionario', null=True)),
                ('promocao_originaria', models.ForeignKey(related_name=b'promocoes_originadas', blank=True, to='comercial.Orcamento', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAcessoComercial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('telefone_celular', models.CharField(max_length=100, blank=True)),
                ('telefone_fixo', models.CharField(max_length=100, blank=True)),
                ('imagem_assinatura', models.ImageField(null=True, upload_to=comercial.models.AssinaturaDir(), blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso ao Comercial',
                'verbose_name_plural': 'Perfis de Acesso ao Comercial',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PropostaComercial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'aberta', max_length=100, blank=True, choices=[(b'aberta', b'Aberta'), (b'convertida', b'Convertida'), (b'perdida', b'Perdida'), (b'perdida_aguardando', b'Perdida: Aguardando Aprova\xc3\xa7\xc3\xa3o')])),
                ('probabilidade', models.IntegerField(default=50, null=True, verbose_name=b'Probabilidade (%)', blank=True)),
                ('probabilidade_inicial', models.IntegerField(default=50, null=True, verbose_name=b'Probabilidade Inicial (%)', blank=True)),
                ('valor_proposto', models.DecimalField(max_digits=10, decimal_places=2)),
                ('valor_fechado', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('data_expiracao', models.DateField(default=datetime.date(2014, 9, 23), verbose_name=b'Data de Expira\xc3\xa7\xc3\xa3o desta Proposta')),
                ('lucro', models.IntegerField(default=0, verbose_name=b'Lucro (%)')),
                ('administrativo', models.IntegerField(default=0, verbose_name=b'Taxa Administrativa (%)')),
                ('impostos', models.IntegerField(default=0, verbose_name=b'Impostos (%)')),
                ('nome_do_proposto', models.CharField(max_length=100, blank=True)),
                ('documento_do_proposto', models.CharField(max_length=100, blank=True)),
                ('rua_do_proposto', models.CharField(max_length=100, blank=True)),
                ('bairro_do_proposto', models.CharField(max_length=100, blank=True)),
                ('cep_do_proposto', models.CharField(max_length=100, blank=True)),
                ('cidade_do_proposto', models.CharField(max_length=100, blank=True)),
                ('endereco_obra_proposto', models.TextField(blank=True)),
                ('representante_legal_proposto', models.CharField(max_length=100, blank=True)),
                ('telefone_contato_proposto', models.CharField(max_length=100, blank=True)),
                ('email_proposto', models.CharField(max_length=100, blank=True)),
                ('objeto_proposto', models.TextField(blank=True)),
                ('descricao_items_proposto', models.TextField(blank=True)),
                ('items_nao_incluso', models.TextField(blank=True)),
                ('forma_pagamento_proposto', models.TextField(blank=True)),
                ('garantia_proposto', models.TextField(blank=True)),
                ('definido_perdido_em', models.DateTimeField(null=True, blank=True)),
                ('definido_perdido_motivo', models.TextField(verbose_name='Motivo de Perda da Proposta', blank=True)),
                ('definido_convertido_em', models.DateTimeField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('cliente', models.ForeignKey(blank=True, to='cadastro.Cliente', null=True)),
                ('contrato_vinculado', models.OneToOneField(null=True, blank=True, to='comercial.ContratoFechado')),
                ('criado_por', models.ForeignKey(related_name=b'proposta_adicionada_set', blank=True, to='rh.Funcionario', null=True)),
                ('definido_convertido_por', models.ForeignKey(related_name=b'proposta_definida_convertida_set', verbose_name='Definido Como Convertido por', blank=True, to='rh.Funcionario', null=True)),
                ('definido_perdido_por', models.ForeignKey(related_name=b'proposta_definida_perdido_set', verbose_name='Definido Como Perdido por', blank=True, to='rh.Funcionario', null=True)),
                ('designado', models.ForeignKey(blank=True, to='rh.Funcionario', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RequisicaoDeProposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.TextField()),
                ('atendido', models.BooleanField(default=False)),
                ('atendido_data', models.DateTimeField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
                ('atendido_por', models.ForeignKey(related_name=b'requisicao_proposta_atendida', blank=True, to='rh.Funcionario', null=True)),
                ('cliente', models.ForeignKey(to='cadastro.Cliente')),
                ('criado_por', models.ForeignKey(related_name=b'proposta_requisitada_set', blank=True, to='rh.Funcionario', null=True)),
                ('proposta_vinculada', models.ForeignKey(blank=True, to='comercial.PropostaComercial', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubGrupoIndicadorDeProdutoProposto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('grupo', models.ForeignKey(to='comercial.GrupoIndicadorDeProdutoProposto')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TabelaDeComissao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor_inicio', models.DecimalField(max_digits=10, decimal_places=2)),
                ('valor_fim', models.DecimalField(max_digits=10, decimal_places=2)),
                ('porcentagem', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TabelaDeParcelamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parcelas', models.IntegerField()),
                ('juros', models.DecimalField(default=0, max_digits=3, decimal_places=2)),
                ('entrada', models.IntegerField(default=0, verbose_name='Entrada (%)')),
            ],
            options={
                'ordering': ['parcelas'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipodeContratoFechado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoDeProposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoRecursoLogistico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='propostacomercial',
            name='parcelamentos_possiveis',
            field=models.ManyToManyField(to='comercial.TabelaDeParcelamento', null=True, verbose_name='Parcelamenos Poss\xedveis', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='propostacomercial',
            name='precliente',
            field=models.ForeignKey(blank=True, to='cadastro.PreCliente', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='propostacomercial',
            name='tipo',
            field=models.ForeignKey(blank=True, to='comercial.TipoDeProposta', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orcamento',
            name='proposta',
            field=models.ForeignKey(blank=True, to='comercial.PropostaComercial', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orcamento',
            name='tabelado_originario',
            field=models.ForeignKey(related_name=b'tabelados_originados', blank=True, to='comercial.Orcamento', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='linharecursomaterial',
            name='orcamento',
            field=models.ForeignKey(to='comercial.Orcamento'),
            preserve_default=True,
        ),
    ]
