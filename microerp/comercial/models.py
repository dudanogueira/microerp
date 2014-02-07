# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '0.0.1'

import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from django.db.models import Sum

from cadastro.models import Cliente
from rh.models import Funcionario

import urllib2

from django.db.models import signals

from django.contrib import messages

from icalendar import Calendar, Event

PROPOSTA_COMERCIAL_STATUS_CHOICES = (
    ('aberta', 'Aberta'),
    ('convertida', 'Convertida'),
    ('perdida', 'Perdida'),
)

CONTRATO_FORMA_DE_PAGAMENTO_CHOICES = (
    ('boleto', 'Boleto'),
    ('credito', u'Cartão de Crédito'),
    ('debito', u'Cartão de Débito'),
    ('dinheiro', 'Dinheiro'),
    ('cheque', 'Cheque'),
    ('permuta', 'Permuta'),
)

CONTRATO_TIPO_CHOICES = (
    ('aberto', 'Aberto'),
    ('fechado', 'Fechado'),
    ('mensal', 'Mensal'),
)

CONTRATO_STATUS_CHOICES = (
    ('cancelado', 'Cancelado'),
    ('emanalise', 'Em Análise'),
    ('invalido', u'Inválido'),
    ('assinatura', u'Aguardando Assinatura'),
    ('emaberto', 'Em Aberto'),
    ('lancado', u'Contrato Lançado'),
    
)

class PropostaComercial(models.Model):

    def __unicode__(self):
            if self.cliente:
                proposto = 'cliente'
                obj = self.cliente
            else:
                proposto = 'precliente'
                obj = self.precliente
            return u"Proposta #%s para %s %s de R$%s com %s%% de probabilidade criado por %s" % (self.id, proposto, obj, self.valor_proposto, self.probabilidade, self.criado_por)
    
    def texto_descricao_items(self):
        texto = ''
        for orcamento in self.orcamentos_ativos():
            texto += "%s\n" % orcamento.descricao 
        return texto
    
    def expirada(self):
        if datetime.date.today() >= self.data_expiracao:
            return True
        else:
            return False

    def ultimo_followup(self):
        if self.followupdepropostacomercial_set.all():
            return self.followupdepropostacomercial_set.all().order_by('-criado')[0]
        else:
            return False

    def dono(self):
        return self.cliente or "Pré Cliente: %s" % self.precliente
    
    def sugere_data_reagendamento_expiracao(self):
        return self.data_expiracao + datetime.timedelta(days=getattr(settings, 'EXPIRACAO_FOLLOWUP_PADRAO', 7))
    
    def orcamentos_ativos(self):
        return self.orcamento_set.filter(ativo=True)
    
    def orcamentos_inativos(self):
        return self.orcamento_set.filter(ativo=False)
    
    def consolidado(self):
        '''soma todos os valores de orcamentos ativos presentes'''
        return self.orcamento_set.filter(ativo=True).aggregate(Sum("custo_total"))['custo_total__sum']

    def clean(self):
        if self.status == 'convertida' and self.definido_convertido_em is None:
              raise ValidationError('Para ser convertida, uma proposta deve possuir a data de conversão.')
    
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    status = models.CharField(blank=True, max_length=100, choices=PROPOSTA_COMERCIAL_STATUS_CHOICES, default='aberta')
    probabilidade = models.IntegerField("Probabilidade (%)", blank=True, null=True, default=50)
    probabilidade_inicial = models.IntegerField("Probabilidade Inicial (%)", blank=True, null=True, default=50)
    valor_proposto = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fechado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_expiracao = models.DateField("Data de Expiração desta Proposta", blank=False, null=False, default=datetime.date.today()+datetime.timedelta(days=getattr(settings, 'EXPIRACAO_FOLLOWUP_PADRAO', 7)))
    observacoes = models.TextField("Observações", blank=False, null=False)
    designado = models.ForeignKey("rh.Funcionario", blank=True, null=True)
    # dados para impressao
    nome_do_proposto = models.CharField(blank=True, max_length=100)
    documento_do_proposto = models.CharField(blank=True, max_length=100)
    rua_do_proposto = models.CharField(blank=True, max_length=100)
    bairro_do_proposto = models.CharField(blank=True, max_length=100)
    cep_do_proposto = models.CharField(blank=True, max_length=100)
    cidade_do_proposto = models.CharField(blank=True, max_length=100)
    endereco_obra_proposto = models.TextField(blank=True)
    representante_legal_proposto = models.CharField(blank=True, max_length=100)
    telefone_contato_proposto = models.CharField(blank=True, max_length=100)
    email_proposto = models.CharField(blank=True, max_length=100)
    objeto_proposto = models.TextField(blank=True)
    descricao_items_proposto = models.TextField(blank=True)
    items_nao_incluso = models.TextField(blank=True)
    forma_pagamento_proposto = models.TextField(blank=True)
    garantia_proposto = models.TextField(blank=True)
    # definido perdido
    definido_perdido_por = models.ForeignKey('rh.Funcionario', verbose_name=u"Definido Como Perdido por", related_name="proposta_definida_perdido_set", blank=True, null=True)
    definido_perdido_em = models.DateTimeField(blank=True, null=True)
    definido_perdido_motivo = models.TextField(u"Motivo de Perda da Proposta", blank=True)
    # definido convertido
    definido_convertido_por = models.ForeignKey('rh.Funcionario', verbose_name=u"Definido Como Convertido por", related_name="proposta_definida_convertida_set", blank=True, null=True)
    definido_convertido_em = models.DateTimeField(blank=True, null=True)
    # contrato fechado vinculado
    contrato_vinculado = models.OneToOneField('ContratoFechado', primary_key=False, blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="proposta_adicionada_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class FollowUpDePropostaComercial(models.Model):
    
    def __unicode__(self):
        return u"Follow Up da Proposta #%s" % self.proposta.id
    
    def data(self):
        return self.criado
        
    class Meta:
        ordering = ['-criado']
    
    proposta = models.ForeignKey('PropostaComercial')
    texto = models.TextField(blank=False)
    reagenda_data_expiracao = models.BooleanField("Reagenda Nova Data de Expiração", default=False)
    data_expiracao = models.DateField("Data de Expiração", blank=False, default=datetime.datetime.today()+datetime.timedelta(days=getattr(settings, 'EXPIRACAO_FOLLOWUP_PADRAO', 7)))
    probabilidade = models.IntegerField("Probabilidade (%)", blank=True, null=True)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class PerfilAcessoComercial(models.Model):
    '''Perfil de Acesso ao Comercial'''
    class Meta:
        verbose_name = u"Perfil de Acesso ao Comercial"
        verbose_name_plural = u"Perfis de Acesso ao Comercial"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    telefone_celular = models.CharField(blank=True, max_length=100)
    telefone_fixo = models.CharField(blank=True, max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

# ORCAMENTO / REQUISICAO DE RECURSOS
class Orcamento(models.Model):
    '''Recurso que pode ser estoque.Produto e rh.Funcionario'''
    
    def __unicode__(self):
        return "%s - R$ %s" % (self.descricao, self.custo_total)
    
    def reajusta_custo(self):
        '''Atualiza o custo de todas as linhas e geral'''
        custo_total = 0
        for linha in self.linharecursomaterial_set.all():
            linha.custo_unitario = linha.produto.preco_venda
            linha.custo_total = linha.produto.preco_venda * linha.quantidade
            linha.save()
            custo_total += linha.custo_total
        #
        self.custo_total = custo_total
        self.save()
        return self.custo_total

    def recalcula_custo_total(self, save=True):
        self.custo_material = self.linharecursomaterial_set.aggregate(total=Sum('custo_total'))['total'] or 0
        self.custo_humano = self.linharecursohumano_set.aggregate(total=Sum('custo_total'))['total'] or 0
        self.custo_total = self.custo_material + self.custo_humano
        if save:
            self.save()
    
    descricao = models.CharField(u"Descrição", blank=True, max_length=100)
    proposta = models.ForeignKey('PropostaComercial', blank=True, null=True)
    selecionado = models.BooleanField(default=True)
    modelo = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    # custos
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_material = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_mao_de_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="orcamento_criado_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class LinhaRecursoMaterial(models.Model):
    
    orcamento = models.ForeignKey('Orcamento')
    produto = models.ForeignKey('estoque.Produto')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,  default=0)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class LinhaRecursoHumano(models.Model):
    orcamento = models.ForeignKey('Orcamento')
    cargo = models.ForeignKey('rh.Cargo')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    quantidade = models.IntegerField(blank=True, null=True, verbose_name="Quantidade de Horas")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class CategoriaContratoFechado(models.Model):
    
    def __unicode__(self):
        return self.nome
    nome = models.CharField(blank=True, max_length=200)

class ContratoFechado(models.Model):
    
    
    def lancar(self, request=None):
        '''lancar o contrato'''
        if self.status  == 'emaberto':
            # lanca o contrato, vinculando X lancamentos mensais do valor_total do contrato à partir da data de inicio da cobranca
            # valor da parcela
            try:
                # verifica se tem entrada
                if self.valor_entrada != 0:
                    # cria lancamento de entrada
                    lancamento = self.lancamento_set.create(valor_cobrado=self.valor_entrada, peso=0, data_cobranca=datetime.date.today(), modo_recebido=self.forma_pagamento)
                    if request:
                        messages.info(request, u"Sucesso! Lançamento de Entrada para o contrato #%s, valor %s em %s" % (self.pk, self.valor_entrada, lancamento.data_cobranca.strftime("%d/%m/%y")))
                valor_parcela = (self.valor - self.valor_entrada) / self.parcelas
                for peso_parcela in range(1, self.parcelas+1):
                    data_cobranca = self.inicio_cobranca + datetime.timedelta(days=30) * peso_parcela
                    self.lancamento_set.create(valor_cobrado=valor_parcela, peso=peso_parcela, data_cobranca=data_cobranca, modo_recebido=self.forma_pagamento)
                    if request:
                        messages.info(request, u"Sucesso! Lançamento para o contrato #%s, Parcela %s, valor %s, no dia %s realizado" % (self.pk, peso_parcela, valor_parcela, data_cobranca.strftime("%d/%m/%y")))
                # fecha o contrato
                self.status = 'lancado'
                self.concluido = True
                self.save()
            except:
                raise

    def proximo_peso_lancamento(self):
        try:
            ultimo_peso = self.lancamento_set.order_by('-peso')[0].peso
        except:
            ultimo_peso = 0
        proximo_peso = int(ultimo_peso) + 1
        return proximo_peso
    
    def __unicode__(self):
        return u"Contrato #%d  com %s do tipo %s no valor %s (%dx) a começar no dia %s. Situação: %s. Categoria: %s" % \
            (self.id, self.cliente, self.get_tipo_display(), self.valor, self.parcelas, self.inicio_cobranca, self.get_status_display(), self.categoria)
    
    def total_valor_cobrado_lancamentos(self):
        return self.lancamento_set.all().aggregate(Sum('valor_cobrado'))

    def total_valor_recebido_lancamentos(self):
        return self.lancamento_set.all().aggregate(Sum('valor_recebido'))

    def ultimo_lancamento(self):
        try:
            ultimo_lancamento = self.lancamento_set.all().order_by('-criado')[0]
        except:
            ultimo_lancamento = None
        return ultimo_lancamento
    
    cliente = models.ForeignKey('cadastro.Cliente')
    tipo = models.ForeignKey('TipodeContratoFechado', blank=True, null=True)
    categoria = models.ForeignKey('CategoriaContratoFechado', blank=True, null=True)
    objeto = models.TextField(blank=False)
    garantia = models.TextField(blank=True)
    items_incluso = models.TextField("Itens Incluso", blank=True)
    items_nao_incluso = models.TextField("Itens Não Incluso", blank=True)
    forma_pagamento = models.CharField("Forma de Pagamento", blank=False, null=False, max_length=100, default="dinheiro", choices=CONTRATO_FORMA_DE_PAGAMENTO_CHOICES)
    parcelas = models.IntegerField("Quantidade de Parcelas", blank=False, null=False, default=1)
    inicio_cobranca = models.DateField(u"Início da Cobrança", default=datetime.datetime.today)
    valor = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)
    valor_entrada = models.DecimalField("Valor de Entrada", max_digits=10, decimal_places=2, default=0)
    receber_apos_conclusao = models.BooleanField("Receber após a conclusão do Contrato", default=False)
    tipo = models.CharField(blank=False, max_length=100, default="fechado", choices=CONTRATO_TIPO_CHOICES)
    status = models.CharField(u"Status/Situação do Contrato", blank=False, max_length=100, default="emaberto", choices=CONTRATO_STATUS_CHOICES)
    concluido = models.BooleanField(default=False)
    responsavel = models.ForeignKey('rh.Funcionario', verbose_name=u"Responsável pelo Contrato")
    responsavel_comissionado = models.ForeignKey('rh.Funcionario', blank=True, null=True, verbose_name=u"Responsável Comissionado", related_name="contrato_comissionado_set")
    motivo_invalido = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class TipodeContratoFechado(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class FechamentoDeComissao(models.Model):
    
    def valor_total(self):
        return self.contratos.exclude(status="cancelado").aggregate(Sum('valor'))['valor__sum'] or 0
    
    def comissao_tabelada(self, valor=None):
        if valor == None:
            valor = self.valor_total()
        try:
            comissao = TabelaDeComissao.objects.filter(valor_inicio__lte=valor, valor_fim__gte=valor)[0].porcentagem
        except:
            comissao = 0
        return comissao
    
    def comissao_calculada(self):
        valor = self.valor_total()
        valor_calculado = (valor * self.comissao_tabelada(valor)) / 100
        return valor_calculado
    
    comissionado = models.ForeignKey('rh.Funcionario', blank=True, null=True, verbose_name=u"Responsável Comissionado", related_name="fechamento_comissao__set")
    contratos = models.ManyToManyField('ContratoFechado', blank=False, null=False)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
    criado_por = models.ForeignKey('rh.Funcionario',  blank=True, null=True, related_name="fechamento_comissao_criado_set")    

class LancamentoDeFechamentoComissao(models.Model):
    fechamento = models.ForeignKey('FechamentoDeComissao')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)

class TabelaDeComissao(models.Model):
    valor_inicio = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fim = models.DecimalField(max_digits=10, decimal_places=2)
    porcentagem = models.DecimalField(max_digits=10, decimal_places=2)


class RequisicaoDeProposta(models.Model):
    
    def __unicode__(self):
        if self.atendido:
            return u"Requisição de Proposta ATENDIDO para %s" % self.cliente
        else:
            return u"Requisição de Proposta ABERTA para %s" % self.cliente
    
    cliente = models.ForeignKey('cadastro.Cliente')
    descricao = models.TextField(blank=False)
    atendido = models.BooleanField(default=False)
    atendido_data = models.DateTimeField(blank=True, null=True)
    atendido_por = models.ForeignKey("rh.Funcionario", blank=True, null=True, related_name="requisicao_proposta_atendida")
    proposta_vinculada = models.ForeignKey('PropostaComercial', blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="proposta_requisitada_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class GrupoIndicadorDeProdutoProposto(models.Model):
    '''Esse modelo se é vinculada por cada produto para se calcular os indicadores de produtos vendidos'''
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)

class SubGrupoIndicadorDeProdutoProposto(models.Model):
    '''Esse modelo se é vinculada por cada produto para se calcular os indicadores de produtos vendidos'''
    
    def __unicode__(self):
        return "%s - %s" % (self.grupo, self.nome)
    
    nome = models.CharField(blank=True, max_length=100)
    grupo = models.ForeignKey('GrupoIndicadorDeProdutoProposto')


# signals
def proposta_comercial_post_save(signal, instance, sender, **kwargs):
      ''' Atualiza os campos da Proposta Comercial após criacao'''
      # somente criados
      if not kwargs.get('created'):
              return False
      
      instance.probabilidade_inicial = instance.probabilidade
      instance.save()

def follow_up_post_save(signal, instance, sender, **kwargs):
    '''Após criar o o FollowUp, atualizar a data de exibicao da proposta se marcado como tal
        e a probabilidade'''

    # somente criados
    if not kwargs.get('created'):
            return False

    if instance.reagenda_data_expiracao:
        instance.proposta.data_expiracao = instance.data_expiracao
    if instance.probabilidade:
        instance.proposta.probabilidade = instance.probabilidade
    else:
        instance.probabilidade = instance.proposta.probabilidade
    instance.proposta.save()

def atualiza_preco_linhas_material(signal, instance, sender, **kwargs):
    '''atualiza o preco das linhas de orcamento'''
    try:
        obj = LinhaRecursoMaterial.objects.get(pk=instance.pk)
    except LinhaRecursoMaterial.DoesNotExist:
        instance.custo_unitario = instance.produto.preco_venda
    else:
        if not obj.produto == instance.produto: # Field has changed
            instance.custo_unitario = instance.produto.preco_venda
    
    if instance.quantidade and instance.custo_unitario:
        resultado = instance.custo_unitario * instance.quantidade
    else:
        resultado = 0
    instance.custo_total = resultado

def atualiza_custo_total_orcamento(signal, instance, sender, **kwargs):
    instance.recalcula_custo_total(save=False)

def atualiza_preco_orcamento_pela_linha(signal, instance, sender, **kwargs):
    try:
        instance.orcamento.recalcula_custo_total(save=True)
    except:
        pass

# SIGNALS CONNECTION
signals.post_save.connect(proposta_comercial_post_save, sender=PropostaComercial)
signals.post_save.connect(follow_up_post_save, sender=FollowUpDePropostaComercial)
signals.pre_save.connect(atualiza_preco_linhas_material, sender=LinhaRecursoMaterial)
signals.post_save.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoMaterial)
signals.post_delete.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoMaterial)
signals.pre_save.connect(atualiza_custo_total_orcamento, sender=Orcamento)