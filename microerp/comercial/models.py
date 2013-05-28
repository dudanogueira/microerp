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