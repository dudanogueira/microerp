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
from django_localflavor_br.br_states import STATE_CHOICES
from django.core.exceptions import ValidationError
from django.db import models

from django.conf import settings

from south.modelsinspector import add_introspection_rules

from django_extensions.db.fields import UUIDField

from django_localflavor_br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField


TIPO_CLIENTE_CHOICES = (
    ('pf', u'Pessoa Física'),
    ('pj', u'Pessoa Jurídica'),
)

class PreCliente(models.Model):
    '''
    Um Pre cliente é convertido depois em Cliente
    '''
    
    def __unicode__(self):
        return self.nome
    
    
    class Meta:
        verbose_name = "Pré Cliente"
        verbose_name_plural = "Pré Clientes"
    
    
    cliente_convertido = models.ForeignKey('Cliente', blank=True, null=True)
    nome = models.CharField(blank=False, max_length=300)
    contato = models.CharField(blank=False, max_length=100)
    dados = models.TextField(blank=True)
    # metadata
    adicionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="precliente_lancado_set")
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
    

class Cliente(models.Model):
    u'''
    ====
    Regras de validação definidas neste modelo
    ====
    1: todo cliente do tipo PJ deve possuir CNPJ
    2: todo cliente do tipo PF deve possuir CPF
    '''
    
    def __unicode__(self):
        return u"%s: %s" % (self.get_tipo_display(), self.nome)
        
    
    def clean(self):
        '''Define as regras de preenchimento e validação da Entidade Cliente.        
        e as regras de validação de CPF ou CNPJ
        '''
        # checa confs do PJ
        if self.tipo == "pj":
            if not self.cnpj:
                raise ValidationError(u"Para Clientes do tipo PJ (Pessoa Jurídica) é OBRIGATÓRIO o CNPJ)")
            else:
                try:
                    self.cnpj = BRCNPJField().clean(self.cnpj)
                except:
                    raise ValidationError(u"Número do CNPJ Inválido!")
        # checa confs do PF
        elif self.tipo == "pf":
            if not self.cpf:
                raise ValidationError(u"Para Clientes do tipo PF (Pessoa Física) é OBRIGATÓRIO o CPF)")
            else:
                try:
                    self.cpf = BRCPFField().clean(self.cpf)
                except:
                    raise ValidationError(u"Número do CPF Inválido!")
        if self.telefone_fixo:
            BRPhoneNumberField().clean(self.telefone_fixo)
        if self.telefone_celular:
            BRPhoneNumberField().clean(self.telefone_celular)
        if not self.telefone_fixo and not self.telefone_celular:
            raise ValidationError(u"É obrigatório um contato telefônico!!")
        
    def documento(self):
        if self.tipo == "pj":
            return "CNPJ: %s" % self.cnpj
        else:
            return "CPF: %s" % self.cpf
    
    def nome_curto(self):
        if self.nome:
            nome_parts = self.nome.split(" ")
            if len(nome_parts) >= 2:
                nome_curto = u"%s %s" % (nome_parts[0], nome_parts[-1])
            else:
                nome_curto = u"%s" % self.nome
            return nome_curto
    
    def quantidade_de_solicitacoes(self):
        return self.solicitacaocomercial_set.count()
    
    def logradouro_completo(self):
        string = u"%s, %s, %s - %s, CEP: %s" % (self.rua, self.numero, self.cidade.nome, self.cidade.estado, self.cep)
        return string
    
    def logradouro_completo_busca(self):
        string = u"%s+%s+%s+%s+%s" % (self.rua, self.numero, self.cidade.nome, self.cidade.estado, self.cep)
        return string
        
    def buscar_geoponto(self, endereco):
        latlng = google_latlng.LatLng()
        latlng.requestLatLngJSON(endereco)
        if latlng.lat and latlng.lng:
            return latlng.lat, latlng.lng
        else:
            return False, False

    def criar_geoponto(self):
        lat, lng = self.buscar_geoponto(self.logradouro_completo_busca())
        if lat and lng:
            # geoponto ok, criando referencia cliente
            # TODO melhorar aqui, nem todos os projetos precisam de GEOREF
            try:
                if self.referenciageograficacliente_set.count() == 0:
                    ponto = fromstr("POINT(%s %s)" % (lng, lat))
                    self.referenciageograficacliente_set.create(ponto=ponto)
            except:
                raise
                print "ERRO AO CRIAR O GEOPONTO PARA %s" % self
                pass
    
    uuid = UUIDField()
    id_referencia = models.IntegerField(blank=True, null=True)
    nome = models.CharField(u"Nome do Cliente", blank=False, null=False, max_length=300)
    fantasia = models.CharField(u"Nome de Fantasia", blank=True, null=True, max_length=500)
    tipo = models.CharField(u"Tipo de Cliente", blank=False, null=False, max_length=10, choices=TIPO_CLIENTE_CHOICES)
    cnpj = models.CharField(u"CNPJ", blank=True, null=True, max_length=255)
    inscricao_estadual = models.CharField(blank=True, null=True, max_length=100)
    cpf = models.CharField(u"CPF", blank=True, null=True, max_length=255)
    rg = models.CharField(blank=True, null=True,  max_length=100)
    nascimento = models.DateField(u"Data de Nascimento/Criação", blank=True, null=True)
    ramo = models.ForeignKey("Ramo", blank=True, null=True)
    observacao = models.TextField(u"Observações Gerais", blank=True, null=True)
    origem = models.ForeignKey("ClienteOrigem", blank=True, null=True, verbose_name="Origem do Cliente")
    # contatos
    contato = models.CharField("Nome do Contato", blank=True, max_length=300)
    email = models.EmailField(blank=True, null=True)
    telefone_fixo = models.CharField(blank=True, null=True, max_length=100, help_text="Formato: XX-XXXX-XXXX")
    telefone_celular = models.CharField(blank=True, null=True, max_length=100)
    fax = models.CharField(blank=True, max_length=100)
    funcionario_responsavel = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário Responsável", blank=True, null=True)
    # financeiro
    solicitar_consulta_credito = models.BooleanField("Solicitar Consulta de Crédito", default=False, help_text="Marque esta opção para solicitar uma consulta de crédito")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class EnderecoCliente(models.Model):
    
    def __unicode__(self):
        return u"Endereço ID#%d do Cliente %s" % (self.id, self.cliente.nome)

    class Meta:
        verbose_name = "Endereço de Cliente"
        verbose_name_plural = "Endereços de Clientes"
    

    def save(self, *args, **kwargs):
            if self.principal is False:
                self.principal = None
            super(EnderecoCliente, self).save(*args, **kwargs)

    # cliente
    cliente = models.ForeignKey(Cliente)
    principal = models.NullBooleanField(default=None, unique=True, help_text="Endereço Principal")
    # telefone
    telefone = models.CharField(blank=True, null=True, max_length=100, help_text="Formato: XX-XXXX-XXXX", verbose_name="Telefone Associado")
    # endereço
    cidade = models.ForeignKey("Cidade", blank=False, null=False)
    bairro = models.ForeignKey("Bairro")
    cep = models.CharField(blank=True, max_length=100, verbose_name=u"CEP")
    rua = models.CharField(blank=True, max_length=500, verbose_name=u"Rua")
    numero = models.CharField(blank=True, max_length=100, verbose_name=u"Número")
    complemento = models.CharField(blank=True, max_length=200, verbose_name=u"Complemento")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        


class Ramo(models.Model):

    class Meta:
        verbose_name = "Ramo de Atuação"
        verbose_name_plural = "Ramos de Atuação"


    def __unicode__(self):
        return "Ramo::%s: %s" % (self.get_tipo_display(), self.nome)
        
    '''Profissão ou Ramo do Cliente'''
    nome = models.CharField(blank=False, null=False, max_length=100)
    tipo = models.CharField(u"Tipo de Cliente", blank=False, null=False, max_length=10, choices=TIPO_CLIENTE_CHOICES)

class Cidade(models.Model):
    '''Cidade do Cliente'''
    
    def __unicode__(self):
        return u"%s - %s" % (unicode(self.nome), self.estado)
    
    nome = models.CharField("Nome da Cidade", blank=False, null=False, max_length=100)
    estado = models.CharField(blank=False, null=False, max_length=2, choices=STATE_CHOICES)

class Bairro(models.Model):
    '''Bairro do Cliente'''
    
    def __unicode__(self):
        return u"%s - %s" % (self.nome, self.cidade)
    
    nome = models.CharField("Nome do Bairro", blank=False, null=False, max_length=100)
    cidade = models.ForeignKey("Cidade")

class ClienteOrigem(models.Model):
    
    def __unicode__(self):
        return u"%s" % self.nome
    
    class Meta:
        verbose_name = "Origem do Cliente"
        verbose_name_plural = "Origens dos Clientes"
    
    nome = models.CharField(blank=False, null=False, max_length=100)
    observacao = models.TextField(u"Observações Gerais", blank=True, null=True)

class TipoDeConsultaDeCredito(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    codigo = models.CharField(blank=False, max_length=100, help_text="Código de Identificação: cpf, cnpj, cheque, etc")
    
class ConsultaDeCredito(models.Model):
    
    class Meta:
        verbose_name = u"Consulta de Crédito"
        verbose_name_plural = u"Consultas de Crédito"
    
    realizada = models.BooleanField(default=False)
    cliente = models.ForeignKey(Cliente)
    funcionario_solicitante = models.ForeignKey('rh.Funcionario', related_name="solicitacoes_consulta_credito_set")
    funcionario_executor = models.ForeignKey('rh.Funcionario', related_name="realizacoes_consulta_credito_set")
    data_solicitacao = models.DateTimeField("Data de Solicitação",blank=False, default=datetime.datetime.now)
    data_realizacao = models.DateTimeField("Data de Realização", blank=True, null=True)
    tipo = models.ForeignKey(TipoDeConsultaDeCredito, verbose_name="Tipo da Consulta")
    # resultado final
    regular = models.BooleanField("Situação Regular", default=True)
    # dados de requisicao da consulta
    requisicao = models.CharField("Requisição", blank=False, max_length=400)
    # dados de retorno da consulta
    observacoes = models.TextField(u"Observações", blank=True, null=True)
    dados_originais = models.TextField("Dados Originais", blank=True, null=True, help_text="Este campo deve ser usado para armazenar o retorno de um webservice em seu formato original")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class Recado(models.Model):
    
    def __unicode__(self):
        return "Recado de: %s Para: %s em %s" % (self.remetente, self.destinatario, self.criado)
    
    class Meta:
        ordering = ['-criado',]

    remetente = models.ForeignKey('rh.Funcionario', related_name="recado_enviado_set")
    destinatario = models.ForeignKey('rh.Funcionario', related_name="recado_recebido_set")
    texto = models.TextField(blank=False, verbose_name="Texto do Recado")
    cliente = models.ForeignKey(Cliente, blank=True, null=True, verbose_name="Cliente Associado (opcional)")
    lido = models.BooleanField(default=False)
    lido_em = models.DateTimeField(blank=True, null=True)
    encaminhado = models.BooleanField(default=False)
    encaminhado_data = models.DateTimeField(blank=False, default=datetime.datetime.now)
    # metadata
    adicionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="recado_criado_set")
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class PerfilAcessoRecepcao(models.Model):
    '''Perfil de Acesso à Recepção'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso à Recepção"
        verbose_name_plural = u"Perfis de Acesso à Recepção"
    
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
