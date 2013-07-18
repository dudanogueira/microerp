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

from cadastro.models import Cliente
from rh.models import Funcionario

import urllib2

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
            
            
            return u"Proposta #%s para %s %s de R$%s com %s%% de probabilidade criado por %s" % (self.id, proposto, obj, self.valor_proposto, self.probabilidade, self.adicionado_por)
    
    def expirado(self):
        
        if datetime.datetime.now() > self.data_expiracao:
            return True
        else:
            return False
    
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    status = models.CharField(blank=True, max_length=100, choices=PROPOSTA_COMERCIAL_STATUS_CHOICES, default='aberta')
    probabilidade = models.IntegerField("Probabilidade (%)", blank=True, null=True, default=50)
    valor_proposto = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fechado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_expiracao = models.DateField("Data de Expiração desta Proposta", blank=False, null=False, default=datetime.date.today()+datetime.timedelta(days=15))
    orcamento_vinculado = models.ForeignKey('Orcamento', blank=True, null=True)
    follow_up = models.DateTimeField(blank=True, null=True)
    observacoes = models.TextField("Observações", blank=False, null=False)
    # metadata
    adicionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proposta_adicionada_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class PerfilAcessoComercial(models.Model):
    '''Perfil de Acesso ao Comercial'''
    class Meta:
        verbose_name = u"Perfil de Acesso ao Comercial"
        verbose_name_plural = u"Perfis de Acesso ao Comercial"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

# ORCAMENTO / REQUISICAO DE RECURSOS
class Orcamento(models.Model):
    '''Recurso que pode ser estoque.Produto e rh.Funcionario'''
    descricao = models.CharField(blank=True, max_length=100)
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    modelo = models.BooleanField(default=False)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class LinhaRecursoMaterial(models.Model):
    orcamento = models.ForeignKey('Orcamento')
    produto = models.ForeignKey('estoque.Produto')
    quantidade = models.IntegerField("Quantidade de Produtos", blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

class LinhaRecursoHumano(models.Model):
    orcamento = models.ForeignKey('Orcamento')
    cargo = models.ForeignKey('rh.Cargo')
    quantidade = models.IntegerField(blank=True, null=True, verbose_name="Quantidade de Horas")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

class CategoriaContratoFechado(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=200)

class ContratoFechado(models.Model):
    
    def lancar(self):
        '''lancar o contrato'''
        if self.status  == 'emaberto':
            # lanca o contrato, vinculando X lancamentos mensais do valor_total do contrato à partir da data de inicio da cobranca
            # valor da parcela
            try:
                valor_parcela = self.valor / self.parcelas
                for peso_parcela in range(1, self.parcelas+1):
                    if peso_parcela == 1:
                        data_cobranca = self.inicio_cobranca
                    else:
                        fator = peso_parcela - 1
                        data_cobranca = self.inicio_cobranca + datetime.timedelta(days=30) * fator
                    self.lancamento_set.create(valor_cobrado=valor_parcela, peso=peso_parcela, data_cobranca=data_cobranca)
                # fecha o contrato
                self.status = 'lancado'
                self.save()
            except:
                raise
                
    
    def __unicode__(self):
        return u"Contrato Fechado #%d  com %s do tipo %s no valor %s (%dx) a começar no dia %s. Situação: %s. Categoria: %s" % \
            (self.id, self.cliente, self.get_tipo_display(), self.valor, self.parcelas, self.inicio_cobranca, self.get_status_display(), self.categoria)
    
    cliente = models.ForeignKey('cadastro.Cliente')
    tipo = models.ForeignKey('TipodeContratoFechado')
    categoria = models.ForeignKey('CategoriaContratoFechado')
    forma_pagamento = models.CharField("Forma de Pagamento", blank=False, null=False, max_length=100, default="dinheiro", choices=CONTRATO_FORMA_DE_PAGAMENTO_CHOICES)
    parcelas = models.IntegerField("Quantidade de Parcelas", blank=False, null=False, default=1)
    inicio_cobranca = models.DateField(u"Início da Cobrança", default=datetime.datetime.today)
    valor = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)
    receber_apos_conclusao = models.BooleanField("Receber após a conclusão do Contrato", default=False)
    tipo = models.CharField(blank=False, max_length=100, default="fechado", choices=CONTRATO_TIPO_CHOICES)
    status = models.CharField(u"Status/Situação do Contrato", blank=False, max_length=100, default="emaberto", choices=CONTRATO_STATUS_CHOICES)
    concluido = models.BooleanField(default=False)
    responsavel = models.ForeignKey('rh.Funcionario', verbose_name=u"Responsável pelo Contrato")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

    

class TipodeContratoFechado(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
    