# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
import datetime

class PerfilAcessoProgramacao(models.Model):
    u'''Perfil de Acesso à Programação'''
    
    def __unicode__(self):
        return u"Perfil de Acesso à Programação de %s" % self.user.funcionario
    
    class Meta:
        verbose_name = u"Perfil de Acesso à Programação"
        verbose_name_plural = u"Perfis de Acesso à Programação"
    
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")


class FollowUpDeContrato(models.Model):
    
    def __unicode__(self):
        return u"Follow Up de Contrato #%s, %s" % (self.contrato.id, self.texto)
    
    def data(self):
        return self.criado
        
    class Meta:
        ordering = ['-criado']
    
    contrato = models.ForeignKey('comercial.ContratoFechado')
    texto = models.TextField(blank=False)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_contrato_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
