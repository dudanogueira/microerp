# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
import datetime

from django.core.exceptions import ValidationError


TAREFA_STATUS_DE_EXECUCAO_CHOICES = (
    ('naoiniciado', u'Não Iniciado'),
    ('emandamento', u'Em Andamento'),
    ('pendente', u'Pendente'),
    ('finalizado', u'Finalizado'),
)

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

class TarefaDeProgramacao(models.Model):
    
    def __unicode__(self):
        if self.contrato:
            return u"Tarefa de Programação #%s do Contrato %s no Cliente %s" % (self.id, self.contrato.id, self.contrato.cliente)
        else:
            return u"Tarefa de Programação #%s no Cliente %s" % (self.id, self.cliente)
    
    def clean(self):
        if not self.contrato and not self.cliente:
            raise ValidationError(u"Erro. a Tarefa deve ser vinculada ao menos a Contrato ou Cliente.")
    
    contrato = models.ForeignKey('comercial.ContratoFechado', blank=True, null=True)
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    status_execucao = models.CharField(u"Status da Execução da Tarefa de Programação", blank=False, max_length=100, default="naoiniciado", choices=TAREFA_STATUS_DE_EXECUCAO_CHOICES)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    aguardando_cliente = models.BooleanField(default=False)
    data_aguardando_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_emandamento = models.DateTimeField(blank=True, null=True)
    data_marcado_pendente = models.DateTimeField(blank=True, null=True)
    data_marcado_retorno_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_finalizado = models.DateTimeField(blank=True, null=True)
    data_programada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    funcionarios_participantes = models.ManyToManyField('rh.Funcionario', related_name="contratos_participantes_programacao", blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="tarefa_de_programacao_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
    

class FollowUpDeContrato(models.Model):
    
    def __unicode__(self):
        return u"Follow Up de Contrato #%s, %s" % (self.contrato.id, self.texto)
    
    def data(self):
        return self.criado
        
    class Meta:
        ordering = ['-criado']
    
    contrato = models.ForeignKey('TarefaDeProgramacao')
    texto = models.TextField(blank=False)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_contrato_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
