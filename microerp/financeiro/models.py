import datetime
from django.db import models

from django.conf import settings

class PerfilAcessoFinanceiro(models.Model):
    '''Perfil de Acesso ao Financeiro'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso ao Financeiro"
        verbose_name_plural = u"Perfis de Acesso ao Financeiro"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class Lancamento(models.Model):
    contrato = models.ForeignKey('comercial.ContratoFechado')
    data_cobranca = models.DateField(default=datetime.datetime.today)
    valor_cobrado = models.DecimalField("Valor Cobrado", max_digits=10, decimal_places=2)
    valor_recebido = models.DecimalField("Valor Recebido", max_digits=10, decimal_places=2, blank=True, null=True)
    data_recebido = models.DateField(blank=True, null=True)
    data_recebido_em_conta = models.DateField(blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")