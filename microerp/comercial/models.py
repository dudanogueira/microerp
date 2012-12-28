# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.core.exceptions import ValidationError

from cadastro.models import Cliente
from rh.models import Funcionario

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
    
    def get_from_range(self, start_date, end_date):
        return self.contatocomercial_set.filter(
        (models.Q(inicio__gt=start_date) & models.Q(inicio__lt=end_date)) |
        (models.Q(fim__lt=end_date) & models.Q(fim__gt=start_date)) |
        (models.Q(inicio__lt=start_date) & models.Q(fim__gt=end_date))
    )
    
    nome = models.CharField(blank=False, max_length=100)
    cor = models.CharField(blank=True, max_length=100, help_text="Exemplo: #0cf603")
    cor_do_texto = models.CharField(blank=True, max_length=100, help_text="Exemplo: #FFF")

class ContatoComercial(models.Model):
    
    def __unicode__(self):
        return u"%s: %s. de %s à %s. %s no cliente %s" % (self.tipo, self.nome, self.inicio.strftime("%d/%m/%y %H:%m"), self.fim.strftime("%d/%m/%y %H:%m"), self.get_status_display(), self.cliente) 

    class Meta:
        verbose_name = u"Contato Comercial"
        verbose_name_plural = u"Contatos Comerciais"
    
    def json_event_object(self):
        output = '{"id":"%s","title":"%s: %s","start":"%s","end":"%s","allDay":%s}' % \
                (self.pk, self.tipo.nome, self.nome, self.inicio.strftime("%s"), self.fim.strftime("%s"), str(self.o_dia_todo).lower())
        return output
    
    nome = models.CharField(blank=True, max_length=255)
    cliente = models.ForeignKey(Cliente)
    observacao = models.TextField(blank=True, null=False)
    o_dia_todo = models.BooleanField(default=False)
    inicio = models.DateTimeField(u"Início", blank=True, default=datetime.datetime.now)
    fim = models.DateTimeField(u"Fim", blank=True, default=datetime.datetime.now)
    status = models.CharField(blank=False, null=False, max_length=100, choices=CONTATO_COMERCIAL_STATUS_CHOICES, default="programado") 
    tipo = models.ForeignKey(TipoContatoComercial)
    solicitacao_comercial_convertida = models.ManyToManyField(SolicitacaoComercial, blank=True, null=True, verbose_name="Solicitação Comercial Gerada pelo Contato")
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True)