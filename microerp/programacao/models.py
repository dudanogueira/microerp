# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
import datetime

from django.core.exceptions import ValidationError

TAREFA_STATUS_DE_EXECUCAO_CHOICES = (
    ('naoiniciado', u'Não Iniciado'),
    ('emandamento', u'Em Andamento'),
    ('pendente', u'Pendente'),
    ('clientependente', u'Cliente Pendente'),
    ('atrasado', u'Atrasado'),
    ('finalizado', u'Finalizado'),
)

TIPO_FOLLOWUP_CHOICES = (
    ('informacao', u'Informação'),
    ('inicio_comunicado', u'Início Comunicado'),
    ('emandamento', u'Em Andamento'),
    ('pendente', u'Pendente'),
    ('clientependente', u'Cliente Pendente'),
    ('finalizado', u'Finalizado'),
)

ORDEM_SERVICO_STATUS_CHOICES = (
    ('naoiniciado', 'Não Iniciado'),
    ('comunicadoinicio', 'Início da Ordem de Serviço Comunicado'),
    ('emandamento', 'Em Andamento'),
    ('atrazado', 'Atrazado'),
    ('pendente', 'Pendente'),
    ('finalizado', 'Finalizado'),
    ('comunicadofim', 'Fim da Ordem de Serviço Comunicado'),
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


class OrdemDeServico(models.Model):
    cliente = models.ForeignKey('cadastro.Cliente')
    # valorizacao quando nao possui contrato
    status = models.CharField(blank=True, max_length=100, choices=ORDEM_SERVICO_STATUS_CHOICES, default='naoiniciado')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateTimeField(blank=False)
    data_fim = models.DateTimeField(blank=False)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
    

class TarefaDeProgramacao(models.Model):
    '''Model Objeto que pode dividir o contrato em diversas partes, com diferentes status de execuções, etc'''
    
    def __unicode__(self):
        if self.contrato:
            return u"Tarefa de Programação #%s do Contrato %s no Cliente %s" % (self.id, self.contrato.id, self.contrato.cliente)
        else:
            return u"Tarefa de Programação #%s no Cliente %s" % (self.id, self.cliente)
    
    def clean(self):
        if not self.contrato and not self.ordem_de_servico:
            raise ValidationError(u"Erro. A Tarefa deve ser vinculada ao menos a um Contrato ou uma Ordem de Serviço.")
        if not self.data_inicio and not self.data_fim:
            raise ValidationError(u"Erro. A Tarefa deve Conter Início e Fim.")
        else:
            if self.data_fim < self.data_inicio:
                raise ValidationError(u"Erro. Data de Fim deve ser posterior ao Início.")
    
    class Meta:
        ordering = (('criado',))
    
    contrato = models.ForeignKey('comercial.ContratoFechado', blank=True, null=True)
    ordem_de_servico = models.ForeignKey('OrdemDeServico', blank=True, null=True)
    # outros dados
    titulo = models.CharField(u"Título", blank=True, max_length=100)
    descricao = models.TextField(blank=True, verbose_name=u"Descrição da Atividade")
    status_execucao = models.CharField(u"Status da Execução da Tarefa de Programação", blank=False, max_length=100, default="naoiniciado", choices=TAREFA_STATUS_DE_EXECUCAO_CHOICES)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    aguardando_cliente = models.BooleanField(default=False)
    data_aguardando_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_emandamento = models.DateTimeField(blank=True, null=True)
    data_marcado_pendente = models.DateTimeField(blank=True, null=True)
    data_marcado_retorno_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_finalizado = models.DateTimeField(blank=True, null=True)
    data_programada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    # inicio, fim e participantes
    data_inicio = models.DateTimeField(blank=False)
    data_fim = models.DateTimeField(blank=False)
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
    
    contrato = models.ForeignKey('comercial.ContratoFechado')
    texto = models.TextField(blank=False)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0)
    tipo = models.CharField(blank=True, max_length=100, choices=TIPO_FOLLOWUP_CHOICES)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_contrato_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
