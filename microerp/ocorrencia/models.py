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

from django.conf import settings
from django.db import models

from django.core.exceptions import ValidationError


OCORRENCIA_STATUS_CHOICES = (
    ('aberta', u'Ocorrência Aberta'),
    ('analise', u'Ocorrência em Análise'),
    ('contato', u'Ocorrência em Contato'),
    ('visto', u'Ocorrência em Visto'),
    ('resolvida', u'Ocorrência Resolvida'),
    ('naoresolvido', u'Ocorrência Não Resolvida'),
)

OCORRENCIA_PRIORIDADE_CHOICES = (
    (0, u'Baixa Prioridade'),
    (5, u'Média Prioridade'),
    (10, u'Alta Prioridade'),
)

class Ocorrencia(models.Model):
    
    def __unicode__(self):
        return u"Ocorrência ID#%d status: %s" % (self.id, self.status)
        
    def reclamante(self):
        return self.cliente or self.precliente or self.contato
    
    def contato_principal(self):
        if self.cliente:
            return self.cliente.telefone_fixo or None, self.cliente.telefone_celular or None, self.cliente.fax or None
        elif self.precliente:
            return [self.precliente.contato]
        else:
            return [self.contato]
    
    # cliente / pre cliente / contato
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    contato = models.TextField(blank=True, null=True)
    # ocorrencia
    prioridade = models.IntegerField(blank=False, null=False, default=10, choices=OCORRENCIA_PRIORIDADE_CHOICES)
    descricao = models.TextField(u"Descrição", blank=False, null=False)
    tipo = models.ForeignKey('TipoOcorrencia', verbose_name="Tipo de Ocorrência")
    status = models.CharField(blank=False, max_length=100, choices=OCORRENCIA_STATUS_CHOICES, default="aberta")
    procede = models.BooleanField(default=True)
    nao_procede_porque = models.TextField(blank=True)
    providencia = models.TextField(blank=True)
    resolucao_final = models.TextField(blank=True)
    resolucao_final_data = models.DateTimeField(blank=True, null=True)
    # departamento / abrangencia
    departamentos_afetados = models.ManyToManyField('rh.Departamento', related_name="ocorrencia_afetada_set", blank=True, null=True)
    departamento_direto = models.ForeignKey('rh.Departamento', related_name="ocorrencia_direta_set", blank=True, null=True)
    # responsavel correcao
    responsavel_correcao = models.ForeignKey('rh.Funcionario', related_name="ocorrencia_correcao_set", blank=True, null=True)
    correcao_iniciada = models.DateTimeField(blank=True, null=True)
    responsavel_contato = models.ForeignKey('rh.Funcionario', related_name="ocorrencia_contato_set", blank=True, null=True)
    contato_realizado = models.DateTimeField(blank=True, null=True)
    responsavel_visto = models.ForeignKey('rh.Funcionario', related_name="ocorrencia_visto_set", blank=True, null=True)
    visto_data = models.DateTimeField(blank=True, default=datetime.datetime.now)
    # metadata
    adicionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ocorrencia_adicionada_set",  blank=True, null=True)
    despachado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ocorrencia_despachado_set",  blank=True, null=True)
    despachado_data = models.DateTimeField(blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
    def clean(self):
        # se nao procede, motivo obrigatorio
        if not self.procede and not self.nao_procede_porque:
            raise ValidationError(u"Se a ocorrência não procede, deve ser informado um motivo.")
        # deve haver pelo menos 1 contato
        if not self.cliente and not self.precliente and not self.contato:
            raise ValidationError(u"Se não houver um Cliente ou Pré Cliente Relacionado, deve haver pelo menos um contato")
        if self.cliente and self.precliente:
            raise ValidationError(u"Deve haver um Cliente ou um Pré Cliente, não os dois.")
        if self.status == 'analise' and not self.providencia:
            raise ValidationError(u"Para alterar o status para Análise, deve ser preenchido o campo Providência")
        if self.status == 'resolvida' and not self.resolucao_final:
            raise ValidationError(u"Para alterar o status para Resolvida, deve ser preenchido o campo Resolução Final")
    class Meta:
        ordering = ['criado',]
            

class TipoOcorrencia(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)


class PerfilAcessoOcorrencia(models.Model):
    '''Perfil de Acesso ao RH'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso às Ocorrências"
        verbose_name_plural = u"Perfis de Acesso às Ocorrências"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
