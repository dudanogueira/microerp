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

import datetime, os
from django.db import models
from django.core.exceptions import ValidationError

from django.db.models import signals, Sum

from django.conf import settings

from django.utils.deconstruct import deconstructible

from estoque.models import Produto

CONTROLE_DE_EQUIPAMENTO_STATUS_CHOICES = (
    ("pendente","Controle Pendente"),
    ("fechado","Controle Fechado"),
)

LINHA_CONTROLE_EQUIPAMENTO_STATUS_CHOICES = (
    ("pendente","Retirada Aberta"),
    ("fechado","Retirada Encerrada"),
)



CONTROLE_TIPO_CHOICES = (
    ('epi', 'Controle de EPI'),
    ('ferramenta', 'Controle de Ferramentas'),
)



@deconstructible
class AnexoControleDir(object):

    def __call__(self, instance, filename):
        return os.path.join(
             'controle-de-equipamento/', str(instance.tipo), str(instance.id), filename
             )
anexo_controle_de_equipamento_local = AnexoControleDir()

# Controle de Equipamentos
class ControleDeEquipamento(models.Model):
    
    def __unicode__(self):
        return u"Controle de Movimento (%s) gerado no dia %s para %s" % (self.get_tipo_display(), self.criado, self.funcionario)

    class Meta:
        verbose_name = u"Controle de Equipamento"
        verbose_name_plural = u"Controles de Equipamento"
             
    funcionario = models.ForeignKey('rh.Funcionario', verbose_name="Funcionário Solicitante", help_text="Funcionário responsável pela retirada do equipamento.")
    status = models.CharField(blank=False, max_length=100, default="pendente", choices=CONTROLE_DE_EQUIPAMENTO_STATUS_CHOICES)
    observacao = models.TextField(u"Observação", blank=True)
    tipo = models.CharField(blank=True, max_length=100, choices=CONTROLE_TIPO_CHOICES)
    # arquivo impresso
    arquivo_impresso_assinado = models.FileField(upload_to=anexo_controle_de_equipamento_local, blank=True, null=True)
    data_arquivo_impresso_assinado_recebido = models.DateField(default=datetime.datetime.today)    
    receptor_arquivo_impresso = models.ForeignKey('rh.Funcionario', related_name="autorizacao_controle_equipamento_set", verbose_name=u"Funcionário que Autorizou o Controle", help_text="Funcionário responsável pela entrega do equipamento.", blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', blank=True, null=True, related_name="controledeequipamento_criado_set")
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class LinhaControleEquipamento(models.Model):
    
    def __unicode__(self):
        return u"%s Quantidades de %s" % (self.quantidade, self.produto)
    
    def pendente(self):
        if self.data_previsao_devolucao > datetime.date.today():
            return False
        else:
            return True
    
    def valor_total_consumo(self):
        return self.quantidade * self.produto.preco_consumo
    
    controle = models.ForeignKey(ControleDeEquipamento)
    produto = models.ForeignKey('estoque.Produto')
    unidade = models.CharField(blank=True, max_length=10)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    data_entregue = models.DateField(blank=True, null=True)
    codigo_ca = models.CharField("Código CA", blank=True, null=True, max_length=100)
    data_previsao_devolucao = models.DateField()
    data_devolvido = models.DateField(blank=True, null=True)
    # metadata
    funcionario_receptor = models.ForeignKey('rh.Funcionario', related_name="recepcao_linha_controle_equipamento_set", verbose_name=u"Funcionário que Autorizou o Controle", help_text="Funcionário responsável pela entrega do equipamento.", blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")


# 
# LINHA DE MATERIAIS DO CONTRATO

class ListaMaterialDoContrato(models.Model):
    '''Lista Consolidada que gerencia a quantidade de Material que compoe um contrato
    É com base nessa lista que serão gerados outros dois documentos
    
     - Registro de Material Entregue
     - Solicitação de Compras
    '''
    
    def atualiza_lista(self):
        '''atualiza essa lista conforme os orcamentos da proposta vinculada a este contrato'''
        for k,v in self.contrato.propostacomercial.gera_notacao_lista_materiais().items():
            produto = Produto.objects.get(pk=k)
            linha,created = self.linhalistamaterial_set.get_or_create(produto=produto)
            linha.quantidade_requisitada = v
            linha.save()
    
    def total_materiais_requisitados(self):
        return self.linhalistamaterial_set.aggregate(Sum('quantidade_requisitada'))['quantidade_requisitada__sum']
    
    def total_materiais_atendidos(self):
        return self.linhalistamaterial_set.aggregate(Sum('quantidade_ja_atendida'))['quantidade_ja_atendida__sum']
        
    contrato = models.OneToOneField('comercial.ContratoFechado', blank=True, null=True)
    ativa = models.BooleanField(default=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class LinhaListaMaterial(models.Model):
    lista  = models.ForeignKey(ListaMaterialDoContrato)
    produto = models.ForeignKey('estoque.Produto', null=True, blank=True)
    quantidade_requisitada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade_ja_atendida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")


#
# MATERIAL LIBERADO PARA ENTREGA
#
class ListaMaterialEntregue(models.Model):
    '''Lista Consolidada De materiais Entregues
    '''
    entregue = models.BooleanField(default=False)
    contrato = models.ForeignKey('comercial.ContratoFechado', blank=True, null=True)
    entregue_por = models.ForeignKey("rh.Funcionario", blank=False, null=False, related_name="entregue_por_set")
    entregue_para = models.ForeignKey("rh.Funcionario", blank=False, null=False, related_name="entregue_para_set")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class LinhaListaMaterialEntregue(models.Model):
    lista  = models.ForeignKey(ListaMaterialEntregue)
    produto = models.ForeignKey('estoque.Produto')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

#
# MATERIAL PARA COMPRA
#

class ListaMaterialCompra(models.Model):
    '''Lista Consolidada de Materiais para Compra
    '''
    contrato = models.ForeignKey('comercial.ContratoFechado', blank=True, null=True)
    ativa = models.BooleanField(default=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class LinhaListaMaterialCompra(models.Model):
    lista  = models.ForeignKey(ListaMaterialCompra)
    produto = models.ForeignKey('estoque.Produto')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
