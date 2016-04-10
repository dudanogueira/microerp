from __future__ import unicode_literals

from django.db import models

class TabelaValores(models.Model):

    def __unicode__(self):
        return "Entre %s e %s Placas: R$ %s" % (
            self.quantidade_placas_inicial,
            self.quantidade_placas_final,
            self.valor
        )

    quantidade_placas_inicial = models.IntegerField(blank=True, null=True)
    quantidade_placas_final = models.IntegerField(blank=True, null=True)
    valor = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)

class FormaParcelamento(models.Model):
    nome = models.CharField(blank=False, max_length=100)
    juros = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)
    parcelas = models.IntegerField(blank=True, null=True)
    empresas = models.ManyToManyField('comercial.EmpresaComercial')
