# -*- coding: utf-8 -*-
from django.contrib.gis.db import models

#Modelo de Referência Geográfiaca para os Módulos do microERP

from cadastro.models import Cliente

# Cliente
class ReferenciaGeograficaCliente(models.Model):
    
    def __unicode__(self):
        return u"GEO>Cliente %s" % self.cliente.nome
    
    cliente = models.ForeignKey(Cliente)
    observacao = models.TextField(blank=True)
    ponto = models.PointField()
    objects = models.GeoManager()
