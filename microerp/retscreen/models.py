from __future__ import unicode_literals

from django.db import models

class TabelaValores(models.Model):

    def __unicode__(self):
        return "Entre %s e %s Placas: R$ %s" % (
            self.quantidade_placas_inicial,
            self.quantidade_placas_final,
            self.valor
        )

    quantidade_placas_inicial = models.FloatField(blank=True, null=True)
    quantidade_placas_final = models.FloatField(blank=True, null=True)
    valor = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")


class Financiamento(models.Model):

    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=False, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")


class PorteFinanciamento(models.Model):

    def __unicode__(self):
        return "%s - de %s a %s" % (
            self.financiamento.nome, self.valor_inicial, self.valor_final
        )

    financiamento = models.ForeignKey(Financiamento)
    valor_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class ParcelaFinanciamento(models.Model):
    porte = models.ForeignKey(PorteFinanciamento)
    quantidade = models.IntegerField("Quantidade de Parcelas", blank=False, null=False)
    juros = models.DecimalField(max_digits=5, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class ReajusteEnergiaAno(models.Model):
    def __unicode__(self):
        return "Reajuste de %s%% no ano %s" % (str(self.percentual), str(self.ano))
    ano = models.IntegerField(blank=True, null=True, unique=True)
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")
