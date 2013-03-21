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
from django.core.exceptions import ValidationError

from cadastro.models import Cliente
from rh.models import Funcionario

import urllib2

from icalendar import Calendar, Event

SOLICITACAO_COMERCIAL_STATUS_CHOICES = (
    ('aberta', 'Aberta'),
    ('convertida', 'Convertida'),
    ('perdida', 'Perdida'),
)

CONTATO_COMERCIAL_STATUS_CHOICES = (
    ('programado', 'Programado'),
    ('realizado', 'Realizado'),
    ('cancelado', 'Cancelado'),
    ('reagendado', 'Reagendado'),
)

# Create your models here.
class SolicitacaoComercial(models.Model):
    '''Registra a Solicitação Comercial
    '''
    def __unicode__(self):
        return u"%s - %s" % (self.identificador(), self.cliente)
    
    def clean(self):
        if self.tipo.permite_valor_variavel and not self.valor:
            raise ValidationError(u"O Tipo de Solicitação Comercial escolhido permite valor variável. Neste caso, o campo valor é OBRIGATÓRIO.")

    class Meta:
        verbose_name = u"Solicitação Comercial"
        verbose_name_plural = u"Solicitações Comerciais"
    
    def valor_calculado(self):
        '''calcula o valor conforme o tipo de solicitação'''
        if self.tipo.permite_valor_variavel:
            return self.valor
        else:
            return self.tipo.valor
    
    def identificador(self):
        return "SC#%d" % self.pk

    cliente = models.ForeignKey(Cliente)
    follow_up = models.BooleanField(default=False, help_text=u"Indica se já foi feito contato de Follow Up")
    data_finalizado = models.DateField(u"Data de Finalização / Expiração desta Solicitação Comercial", blank=True, null=True)
    data_convertido = models.DateField(u"Data de Conversão / Fechamento desta Solicitação Comercial", blank=True, null=True)
    observacao = models.TextField(u"Observações Gerais", blank=True, null=True)
    status = models.CharField(u"Situação", blank=False, null=False, default="aberta", max_length=100, choices=SOLICITACAO_COMERCIAL_STATUS_CHOICES)
    tipo = models.ForeignKey("TipoSolicitacaoComercial", blank=False, null=False, verbose_name="Tipo de Solicitação Comercial")
    valor = models.FloatField(blank=True, null=True, help_text="O valor deste campo é sobrescrito caso o Tipo de Solicitação possua um valor fechado")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class TipoSolicitacaoComercial(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    class Meta:
        verbose_name = u"Tipo de Solicitação Comercial"
        verbose_name_plural = u"Tipos de Solicitações Comerciais"

    def clean(self):
        if not self.permite_valor_variavel and not self.valor:
            raise ValidationError(u"Se o Tipo de Solicitação Comercial não permite valor variável, o campo valor é OBRIGATÓRIO")

    nome = models.CharField(blank=False, null=False, max_length=100)
    mao_de_obra_inclusa = models.BooleanField(u"Mão de Obra Inclusa", default=True)
    permite_valor_variavel = models.BooleanField("Permite Valor Variável", default=True)
    valor = models.FloatField(blank=True, null=True, help_text=u"Deixe este campo em branco para permitir a definição do valor na Solicitação Comercial")

class TipoContatoComercial(models.Model):
    
    def __unicode__(self):
        return self.nome
    

    nome = models.CharField(blank=False, max_length=100)
    cor = models.CharField(blank=True, max_length=100, help_text="Exemplo: #0cf603")
    cor_do_texto = models.CharField(blank=True, max_length=100, help_text="Exemplo: #FFF")

class ContatoComercial(models.Model):
    
    def __unicode__(self):
        return u"%s. de %s à %s. %s no cliente %s" % (self.nome, self.inicio.strftime("%d/%m/%y %H:%m"), self.fim.strftime("%d/%m/%y %H:%m"), self.get_status_display(), self.cliente)

    class Meta:
        verbose_name = u"Contato Comercial"
        verbose_name_plural = u"Contatos Comerciais"
    
    def json_event_object(self):
        output = '{"id":"%s","title":"%s: %s","start":"%s","end":"%s","allDay":%s}' % \
                (self.pk, self.agenda_fonte.tipo.nome, self.nome, self.inicio.strftime("%s"), self.fim.strftime("%s"), str(self.o_dia_todo).lower())
        return output
    
    def tipo(self):
        return self.agenda_fonte.tipo
    
    nome = models.CharField(blank=True, max_length=255)
    cliente = models.ForeignKey(Cliente, blank=True, null=True)
    observacao = models.TextField(blank=True, null=False)
    o_dia_todo = models.BooleanField(default=False)
    inicio = models.DateTimeField(u"Início", blank=True, default=datetime.datetime.now)
    fim = models.DateTimeField(u"Fim", blank=True, default=datetime.datetime.now)
    status = models.CharField(blank=False, null=False, max_length=100, choices=CONTATO_COMERCIAL_STATUS_CHOICES, default="programado") 
    solicitacao_comercial_convertida = models.ManyToManyField(SolicitacaoComercial, blank=True, null=True, verbose_name="Solicitação Comercial Gerada pelo Contato")
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True)
    # fonte de agenda
    agenda_fonte = models.ForeignKey('FonteDeAgendaComercial', blank=True, null=True)
    # controle da agenda
    id_referencia = models.CharField(blank=True, max_length=255)
    ultima_alteracao = models.DateTimeField(blank=True, null=True)

class FonteDeAgendaComercial(models.Model):
    
    
    def filtra_intervalo(self, start_date, end_date):
        return self.contatocomercial_set.filter(
        (models.Q(inicio__gt=start_date) & models.Q(inicio__lt=end_date)) |
        (models.Q(fim__lt=end_date) & models.Q(fim__gt=start_date)) |
        (models.Q(inicio__lt=start_date) & models.Q(fim__gt=end_date))
    )
    
    def __unicode__(self):
        return "Fonte de Agenda de %s em %s" % (self.funcionario, self.url)
    
    def atualiza_agenda(self, return_array=False):
        '''Baixa os envetos do URL de ICAL'''
        req = urllib2.urlopen(self.url)
        response = req.read()
        gcal = Calendar.from_ical(response)
        store = []
        for vevent in gcal.walk():
            if vevent.name == "VEVENT":
                store.append(vevent)
                uid = vevent.get('UID')
                titulo = vevent.get('SUMMARY')
                contato,created = ContatoComercial.objects.get_or_create(id_referencia=uid, agenda_fonte=self)
                contato.nome = titulo
                contato.inicio = vevent.get('DTSTART').dt
                contato.fim = vevent.get('DTEND').dt
                contato.save()
        if return_array == True:
            return store
                
        
    descricao = models.CharField("Descrição da Agenda", blank=True, max_length=100)
    url = models.URLField(blank=False)
    tipo = models.ForeignKey(TipoContatoComercial)
    # Funcionário responsável
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True)