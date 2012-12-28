# -*- coding: utf-8 -*-
import datetime
from django.contrib.localflavor.br.br_states import STATE_CHOICES
from django.core.exceptions import ValidationError
from django.db import models

from south.modelsinspector import add_introspection_rules

from django_extensions.db.fields import UUIDField

from django.contrib.localflavor.br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField

TIPO_CLIENTE_CHOICES = (
    ('pf', u'Pessoa Física'),
    ('pj', u'Pessoa Jurírica'),
)

class Cliente(models.Model):
    u'''
    ====
    Regras de validação definidas neste modelo
    ====
    1: todo cliente do tipo PJ deve possuir CNPJ
    2: todo cliente do tipo PF deve possuir CPF
    '''
    
    def __unicode__(self):
        return "%s: %s" % (self.get_tipo_display(), self.nome)
        
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
        BRPhoneNumberField().clean(self.telefone_fixo)
        BRPhoneNumberField().clean(self.telefone_celular)
        
    def documento(self):
        if self.tipo == "pj":
            return "CNPJ: %s" % self.cnpj
        else:
            return "CPF: %s" % self.cpf
    
    def quantidade_de_solicitacoes(self):
        return self.solicitacaocomercial_set.count()
        
    uuid = UUIDField()
    nome = models.CharField(u"Nome do Cliente", blank=False, null=False, max_length=300)
    tipo = models.CharField(u"Tipo de Cliente", blank=False, null=False, max_length=10, choices=TIPO_CLIENTE_CHOICES)
    cnpj = models.CharField(u"CNPJ", blank=True, max_length=255)
    cpf = models.CharField(u"CPF", blank=True, max_length=255)
    nascimento = models.DateField(u"Data de Nascimento/Criação", blank=True, null=True)
    ramo = models.ForeignKey("Ramo")
    observacao = models.TextField(u"Observações Gerais", blank=True, null=True)
    origem = models.ForeignKey("ClienteOrigem", blank=False, null=False, verbose_name="Origem do Cliente")
    # contatos
    email = models.EmailField(blank=True, null=True)
    telefone_fixo = models.CharField(blank=False, max_length=100, null=False, help_text="Formato: XX-XXXX-XXXX")
    telefone_celular = models.CharField(blank=True, max_length=100)
    fax = models.CharField(blank=True, max_length=100)
    # endereço
    cidade = models.ForeignKey("Cidade", blank=False, null=False)
    bairro = models.ForeignKey("Bairro")
    cep = models.CharField(blank=True, max_length=100, verbose_name=u"CEP")
    rua = models.CharField(blank=True, max_length=500, verbose_name=u"Rua")
    numero = models.CharField(blank=True, max_length=100, verbose_name=u"Número")
    complemento = models.CharField(blank=True, max_length=200, verbose_name=u"Complemento")
    # comercial
    # TODO: filtrar o grupo pela info no settings
    #
    funcionario_responsavel = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário Responsável")
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
        return "%s - %s" % (self.nome, self.estado)
    
    nome = models.CharField("Nome da Cidade", blank=False, null=False, max_length=100)
    estado = models.CharField(blank=False, null=False, max_length=2, choices=STATE_CHOICES)

class Bairro(models.Model):
    '''Bairro do Cliente'''
    
    def __unicode__(self):
        return "%s - %s" % (self.nome, self.cidade)
    
    nome = models.CharField("Nome do Bairro", blank=False, null=False, max_length=100)
    cidade = models.ForeignKey("Cidade")

class ClienteOrigem(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Origem do Cliente"
        verbose_name_plural = "Origens dos Clientes"
    
    nome = models.CharField(blank=False, null=False, max_length=100)
    observacao = models.TextField(u"Observações Gerais", blank=True, null=True)

# OAUTH - FOR GOOGLE
from oauth2client.django_orm import FlowField, CredentialsField
from django.contrib.auth.models import User
class FlowModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()

class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()
 
add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField"])
add_introspection_rules([], ["^oauth2client\.django_orm\.FlowField"])
