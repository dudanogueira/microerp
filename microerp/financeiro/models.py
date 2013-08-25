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

#CONTRATO_FORMA_DE_PAGAMENTO_CHOICES = (
#    ('boleto', 'Boleto'),
#    ('credito', u'Cartão de Crédito'),
#    ('debito', u'Cartão de Débito'),
#    ('dinheiro', 'Dinheiro'),
#    ('cheque', 'Cheque'),
#    ('permuta', 'Permuta'),
#)

from comercial.models import CONTRATO_FORMA_DE_PAGAMENTO_CHOICES
LANCAMENTO_MODO_RECEBIDO_CHOICES = CONTRATO_FORMA_DE_PAGAMENTO_CHOICES

from django.conf import settings

LANCAMENTO_SITUACAO_CHOICES = (
    ('a','Aberto'),
    ('r','Recebido'),
    ('p','Pendente'),
    ('t','Antecipado'),
)

import datetime
from django.db import models

from django.conf import settings

class PerfilAcessoFinanceiro(models.Model):
    '''Perfil de Acesso ao Financeiro'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso ao Financeiro"
        verbose_name_plural = u"Perfis de Acesso ao Financeiro"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class ContaBancaria(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)

class Lancamento(models.Model):
    
    def __unicode__(self):
        if self.data_recebido:
            return u"Lançamento #%s de peso %d RECEBIDO em %s por %s do Contrato #%d, Cliente %s de R$%s para %s" % (self.id, self.peso, self.data_recebido, self.recebido_por.funcionario, self.contrato.id, self.contrato.cliente, self.valor_cobrado, self.data_cobranca)
        else:
            if self.antecipado:
                return u"Lançamento #%s de peso %d  Já ANTECIPADO do Contrato #%d, Cliente %s de R$%s para %s" % (self.id, self.peso, self.contrato.id, self.contrato.cliente, self.valor_cobrado, self.data_cobranca)
            else:
                return u"Lançamento #%s de peso %d  A RECEBER do Contrato #%d, Cliente %s de R$%s para %s" % (self.id, self.peso, self.contrato.id, self.contrato.cliente, self.valor_cobrado, self.data_cobranca)

    def clean(self):
        if self.data_recebido and not self.modo_recebido:
            raise ValidationError(u"Erro. Para receber o valor, é preciso especificar o modo recebido")
        
        # contrato aberto, valor_cobrado deve ser igual a soma
        # da mao de obra e materiais
        if self.contrato.tipo == 'aberto' and self.valor_mao_de_obra and self.valor_materiais:
            self.valor_cobrado = self.valor_mao_de_obra + self.valor_materiais
    
    class Meta:
        unique_together = (('contrato', 'peso'),)
        ordering = ('data_cobranca',)
    
    def pendente(self):
        if self.data_cobranca < datetime.date.today():
            return True
        else:
            return False
    
    def juros(self):
        '''calcula o valor incidido de juros neste lancamento'''
        porcentagem_juros = getattr(settings, 'JUROS', 10)
        if self.pendente():
            dias = datetime.date.today() - self.data_cobranca
            dias = dias.days
            juros = self.valor_cobrado * porcentagem_juros / 100
            return juros * dias
        else:
            return 0
    
    def multa(self):
        if self.pendente():
            porcentagem_multa = getattr(settings, 'MULTA', 50)
            multa = self.valor_cobrado * porcentagem_multa / 100
            return multa
        else:
            return 0
    
    def total_pendente(self):
        if self.pendente():
            return self.valor_cobrado + self.juros() + self.multa()
        else:
            if self.antecipado:
                return self.valor_recebido
            else:
                return self.valor_cobrado

    def antecipavel(self):
        
        antecipaveis = getattr(settings, 'TIPOS_LANCAMENTOS_ANTECIPAVEIS', ('boleto', 'cheque', 'credito'))
        if self.modo_recebido in antecipaveis and not self.pendente():
            return True
        else:
            return False
    
    contrato = models.ForeignKey('comercial.ContratoFechado')
    peso = models.IntegerField(blank=False, null=False, default=1)
    situacao = models.CharField(blank=False, default="a", choices=LANCAMENTO_SITUACAO_CHOICES, max_length=1)
    informacoes_pagamento = models.TextField(u"Informações sobre o Pagamento", blank=True)
    # cobranca
    data_cobranca = models.DateField(default=datetime.datetime.today)
    valor_cobrado = models.DecimalField("Valor Cobrado", max_digits=10, decimal_places=2)
    # recebimento
    valor_recebido = models.DecimalField("Valor Recebido", max_digits=10, decimal_places=2, blank=True, null=True)
    modo_recebido = models.CharField(blank=False, null=False, max_length=100, choices=LANCAMENTO_MODO_RECEBIDO_CHOICES)
    data_recebido = models.DateField(blank=True, null=True)
    recebido_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="lancamento_recebido_set", blank=True, null=True)
    # conciliacao - recebido em conta
    data_recebido_em_conta = models.DateField(blank=True, null=True)
    conta = models.ForeignKey('ContaBancaria', blank=True, null=True)
    conciliado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="lancamento_conciliado_set", blank=True, null=True)
    # antecipacao
    data_antecipado = models.DateField(u"Data da Antecipação", blank=True, null=True)
    antecipado = models.BooleanField(default=False)
    antecipado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="lancamento_antecipado_set", blank=True, null=True)
    # contrato aberto
    valor_mao_de_obra = models.DecimalField("Valor da Mão de Obra", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_materiais = models.DecimalField("Valor de Materiais", max_digits=10, decimal_places=2, blank=True, null=True)
    notas_fiscais = models.TextField(blank=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class ObservacaoLancamento(models.Model):
    
    def __unicode__(self):
        return u"Observação ao lançamento %s: %s" % (self.lancamento, self.texto)
    
    class Meta:
        ordering = ('-criado',)
    
    lancamento = models.ForeignKey('Lancamento')
    texto = models.TextField(blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class ProcessoAntecipacao(models.Model):
    
    def __unicode__(self):
        return u"Processo de Antecipação #%s criado por %s no dia %s" % (self.id, self.antecipado_por.funcionario, self.criado)
    
    valor_inicial = models.DecimalField(u"Valor Inicial dos Lançamentos Antecipados", max_digits=10, decimal_places=2, blank=False, null=False)
    percentual_abatido = models.DecimalField(u"Percentual Abatido do Valor", max_digits=10, decimal_places=2, blank=False, null=False)
    valor_abatido = models.DecimalField(u"Valor Abatido dos Lançamentos Antecipados", max_digits=10, decimal_places=2, blank=False, null=False)
    lancamentos = models.ManyToManyField('Lancamento')
    antecipado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
     
    