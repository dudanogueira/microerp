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
from localflavor.br.br_states import STATE_CHOICES
from django.core.exceptions import ValidationError
from django.db import models

from django.conf import settings

from south.modelsinspector import add_introspection_rules

from django_extensions.db.fields import UUIDField

from localflavor.br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField


TIPO_CLIENTE_CHOICES = (
    ('pf', u'Pessoa Física'),
    ('pj', u'Pessoa Jurídica'),
)

RECADO_TIPO_CHOICES = (
    ('compra', 'Solicitação de Compra'),
    ('ocorrencia', 'Registro de Ocorrência'),
    ('comercial', 'Solicitação Comercial'),
    ('informacao_geral', u'Solicitação de Informação'),
    ('ofertar_produto', u'Oferta de Produto'),
    ('agendamento_reuniao', u'Agendamento de Reunião'),
    ('informacao_projeto', u'Informação sobre Projeto'),
)

class PreClienteSemInteresseOpcao(models.Model):
    
    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=True, max_length=100)

class PreCliente(models.Model):
    '''
    Um Pre cliente é convertido depois em Cliente
    '''
    def __unicode__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Pré Cliente"
        verbose_name_plural = "Pré Clientes"
    
    def propostas_abertas(self):
        return self.propostacomercial_set.filter(status="aberta", data_expiracao__gte=datetime.date.today())
    
    def propostas_expiradas(self):
        return self.propostacomercial_set.filter(status="aberta", data_expiracao__lt=datetime.date.today())
    
    def propostas_convertidas(self):
        return self.propostacomercial_set.filter(status="convertida")
    
    def propostas_perdidas(self):
        return self.propostacomercial_set.filter(status__in=("perdida", "perdida_aguardando"))
    
    
    
    cliente_convertido = models.OneToOneField('Cliente', blank=True, null=True)
    nome = models.CharField(blank=False, max_length=300)
    contato = models.CharField(blank=False, max_length=100)
    dados = models.TextField(blank=True)
    designado = models.ForeignKey('rh.Funcionario', blank=True, null=True, verbose_name="Funcionário Designado", related_name="precliente_designado_set")
    # metadata
    sem_interesse = models.BooleanField(default=False)
    sem_interesse_motivo = models.TextField("Motivo do Desinteresse", blank=True,)
    sem_interesse_opcao = models.ForeignKey('PreClienteSemInteresseOpcao', blank=True, null=True, verbose_name="Opção de Desinteresse")
    sem_interesse_data = models.DateTimeField(blank=True, default=datetime.datetime.now)
    data_convertido = models.DateField(blank=True, null=True)
    convertido_por = models.ForeignKey('rh.Funcionario', related_name="precliente_convertido_set", blank=True, null=True)
    adicionado_por = models.ForeignKey('rh.Funcionario', related_name="precliente_lancado_set")
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class PerfilClienteLogin(models.Model):
    '''
    Perfil para login do cliente na interface do sistema.
    Se nao possui esse perfil, o cliente não pode logar
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="Usuário do Sistema", blank=True, null=True)
    cliente = models.OneToOneField('Cliente', verbose_name="Cliente Cadastrado no Sistema", blank=True, null=True)
    # metadata
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
        if self.telefone_fixo:
            BRPhoneNumberField().clean(self.telefone_fixo)
        if self.telefone_celular:
            BRPhoneNumberField().clean(self.telefone_celular)
        if self.cnpj and self.cnpj == '0'*14:
            raise ValidationError({'cnpj': [u'Embora Válido, não é aceito um CNPJ com %s ;' % '000000000000000',]})
        
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
        if self.enderecocliente_set.all():
            if self.enderecocliente_set.filter(principal=True):
                endereco = self.enderecocliente_set.filter(principal=True)[0]
            else:
                endereco = self.enderecocliente_set.all()[0]
            string = u"%s, %s, %s - %s, CEP: %s" % (endereco.rua, endereco.numero, endereco.bairro.cidade.nome, endereco.bairro.cidade.estado, endereco.cep)
        else: 
            string = None
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

    def propostas_abertas(self):
        return self.propostacomercial_set.filter(status="aberta", data_expiracao__gte=datetime.date.today())
    
    def propostas_expiradas(self):
        return self.propostacomercial_set.filter(status="aberta", data_expiracao__lt=datetime.date.today())
    
    def propostas_convertidas(self):
        return self.propostacomercial_set.filter(status="convertida")
    
    def propostas_perdidas(self):
        return self.propostacomercial_set.filter(status__in=["perdida", "perdida_aguardando"])
    
    def requisicao_proposta_abertas(self):
        return self.requisicaodeproposta_set.filter(atendido=False)
    
    def requisicao_proposta_atendidas(self):
        return self.requisicaodeproposta_set.filter(atendido=True)
    
    def endereco_principal(self):
        if self.enderecocliente_set.filter(principal=True):
            endereco = self.enderecocliente_set.filter(principal=True).first()
        elif self.enderecocliente_set.first():
            endereco = self.enderecocliente_set.first()
        else:
            endereco = None
        return endereco
    
    def qualquer_telefone(self):
        if self.telefone_fixo:
            return self.telefone_fixo
        elif self.telefone_celular:
            return self.telefone_celular
        else:
            telefones = self.enderecocliente_set.exclude(telefone=None)
            if telefones:
                return self.enderecocliente_set.exclude(telefone=None).first().telefone
            else:
                return None
    
    uuid = UUIDField()
    ativo = models.BooleanField(default=True)
    id_referencia = models.IntegerField(blank=True, null=True)
    id_referencia_criado = models.BooleanField(default=False, help_text="Indica se o id de referencia foi criado pelo sistema")
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
    # financeiro
    solicitar_consulta_credito = models.BooleanField("Solicitar Consulta de Crédito", default=False, help_text="Marque esta opção para solicitar uma consulta de crédito")
    conceder_credito = models.BooleanField(default=True)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # comercial - designacao
    designado = models.ForeignKey('rh.Funcionario', verbose_name="Funcionário Designado", related_name="cliente_designado_set", blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class EnderecoCliente(models.Model):
    
    def __unicode__(self):
        return u"Endereço ID#%s do Cliente %s" % (self.id, self.cliente.nome)

    class Meta:
        verbose_name = "Endereço de Cliente"
        verbose_name_plural = "Endereços de Clientes"
        unique_together = ('principal', 'cliente')
        ordering = ('-principal',)

    def save(self, *args, **kwargs):
            if self.principal is False:
                self.principal = None
            super(EnderecoCliente, self).save(*args, **kwargs)

    # cliente
    cliente = models.ForeignKey(Cliente)
    principal = models.NullBooleanField(default=None, help_text="Endereço Principal")
    # telefone
    telefone = models.CharField(blank=True, null=True, max_length=100, help_text="Formato: XX-XXXX-XXXX", verbose_name="Telefone Associado")
    # endereço
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
        
    class Meta:
        ordering = ['nome']
    
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
        return u"Recado de: %s Para: %s em %s" % (self.remetente, self.destinatario, self.criado)
    
    class Meta:
        ordering = ['-criado',]

    def clean(self):
        if self.tipo == "outros" and not self.tipo_outros:
            raise ValidationError(u"Se Tipo de Recado é 'Outros', descreva-o.")

    remetente = models.ForeignKey('rh.Funcionario', related_name="recado_enviado_set")
    destinatario = models.ForeignKey('rh.Funcionario', related_name="recado_recebido_set")
    texto = models.TextField(blank=False, verbose_name="Texto do Recado")
    tipo = models.CharField("Tipo de Recado", blank=False, max_length=100, choices=RECADO_TIPO_CHOICES, default="comercial")
    tipo_outros = models.TextField(blank=True)
    cliente = models.ForeignKey(Cliente, blank=True, null=True, verbose_name="Cliente Associado (opcional)")
    lido = models.BooleanField(default=False)
    lido_em = models.DateTimeField(blank=True, null=True)
    email_enviado = models.BooleanField(default=False) 
    encaminhado = models.BooleanField(default=False)
    encaminhado_data = models.DateTimeField(blank=False, default=datetime.datetime.now)
    # metadata
    adicionado_por = models.ForeignKey('rh.Funcionario', related_name="recado_criado_set")
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

class EnderecoEmpresa(models.Model):
    '''unidade da empresa (matriz, filial, etc)'''
    
    def __unicode__(self):
        return u"%s" % self.nome

    cnpj_vinculado = models.CharField(blank=True, max_length=100)
    nome = models.CharField(blank=False, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
    