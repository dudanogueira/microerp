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

from django.db.models import signals

CONTROLE_DE_EQUIPAMENTO_STATUS_CHOICES = (
    ("pendente","Controle Pendente"),
    ("fechado","Controle Fechado"),
)

LINHA_CONTROLE_EQUIPAMENTO_STATUS_CHOICES = (
    ("pendente","Retirada Aberta"),
    ("fechado","Retirada Encerrada"),
)

# Controle de Equipamentos
class ControleDeEquipamento(models.Model):
    
    def __unicode__(self):
        return u"Controle de Movimento de Equipamento gerado no dia %s para %s" % (self.criado, self.funcionario)
    
    class Meta:
        verbose_name = u"Controle de Equipamento"
        verbose_name_plural = u"Controles de Equipamento"
    
    
    def alocar_material(self):
        '''marca todos os produtos equipamentos presentes na linha como alocado'''
        for linha in self.linhacontroledeequipamento_set.all():
            linha.equipamento.alocado = True
            linha.equipamento.save()
    
    def liberar_material(self):
        for linha in self.linhacontroledeequipamento_set.all():
            linha.equipamento.alocado = False
            linha.equipamento.save()
    
    funcionario = models.ForeignKey('rh.Funcionario', verbose_name="Funcionário Solicitante", help_text="Funcionário responsável pela retirada do equipamento.")
    status = models.CharField(blank=False, max_length=100, default="pendente", choices=CONTROLE_DE_EQUIPAMENTO_STATUS_CHOICES)
    observacao = models.TextField(blank=True)
    # metadata
    autorizador = models.ForeignKey('rh.Funcionario', related_name="autorizacao_controle_equipamento_set", verbose_name=u"Funcionário que Autorizou o Controle", help_text="Funcionário responsável pela entrega do equipamento.", blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class TipoDeEquipamento(models.Model):
    
    def __unicode__(self):
        return "%s" % self.nome
    
    nome = models.CharField("Nome do Tipo de Equipamento", blank=True, max_length=100, help_text="Ex: Uniforme/EPI, Ferramentas, Insumo para Escritório, Insumo para Limpeza, etc.")

class Produto(models.Model):
    
    def __unicode__(self):
        if self.consumivel:
            return u"%s em (%s) - Consumível" % (self.nome, self.medida)
        else:
            return u"%s em (%s) - Não Consumível" % (self.nome, self.medida)
            
    nome = models.CharField("Nome do Produto", blank=True, max_length=100, help_text="Ex: Martelo, Fita Adesiva, Detergente, etc.")
    medida = models.CharField(u"Unidade de Medida", blank=False, max_length=100)
    consumivel = models.BooleanField(default=False, help_text="Caso seja consumível, deverá ser fornecida uma nova quantidade na devolução do equipamento.")    
    estoque_minimo_total = models.IntegerField(blank=True, null=True)

class Equipamento(models.Model):
    
    def __unicode__(self):
        if self.alocado:
            alocado = " ALOCADO "
        else:
            alocado = ""
        return "#%s %s- %s %s de %s/%s %s" % (self.id, alocado, self.quantidade, self.produto.medida, self.produto, self.marca, self.modelo)
    
    def consumivel(self): 
        return self.produto.consumivel
    
    produto = models.ForeignKey(Produto)
    # controle da propriedade
    perdido = models.BooleanField(default=False)
    data_perdido = models.DateField("Data que foi identificado o sumiço deste produto", blank=True, null=True)
    alocado = models.BooleanField(default=False, help_text="Campo preenchido automáticamente conforme o processo de entrada/saída")
    data_de_compra = models.DateField("Data de Compra do Produto", default=datetime.datetime.today)
    data_expiracao = models.DateField("Data de Expiração deste Produto", blank=True, null=True)
    # controle da especificação
    modelo = models.CharField(blank=True, max_length=100)
    marca = models.CharField(blank=False, max_length=100)
    tipo = models.ForeignKey(TipoDeEquipamento)    
    quantidade = models.IntegerField("Quantidade atual/inicial.", blank=False, null=False, default=0, help_text="Caso seja 0, será ignorado/não alocado.")
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class LinhaControleDeEquipamento(models.Model):
    
    def __unicode__(self):
        return u"Linha do %s do equipamento %s" % (self.controle, self.equipamento)
    
    class Meta:
        verbose_name = "Linha de Controle de Equipamento"
        verbose_name_plural = "Linhas de Controle de Equipamento"
        unique_together = (('controle', 'equipamento'))
    
    def clean(self):
        if self.devolvido or self.status == "fechado":
            if not self.devolvido:
                raise ValidationError(u"Para encerrar a retirada do item de Equipamento é necessário marcar como devolvido.")
            if self.status != "fechado":
                raise ValidationError(u"Para marcar um item de Equipamento como devolvido é necessário alterar o status para Retirada Encerrada")
            if not self.receptor:
                raise ValidationError(u"Ao marcar um item de Equipamento como devolvido, deverá ser informado o FUNCIONÁRIO RECEPTOR!")
            if not self.data_devolucao_efetiva:
                raise ValidationError(u"Ao marcar um item de Equipamento como devolvido, deverá ser informado a DATA DE DEVOLUÇÃO REALIZADA!")
            if self.equipamento.produto.consumivel and not self.quantidade_devolvida:
                raise ValidationError(u"Ao marcar um item de Equipamento como devolvido, deverá ser informado a QUANTIDADE DEVOLVIDA!")
            if not self.devolutor:
                self.devolutor = self.controle.funcionario
    
    def diferenca_quantidade(self):
        if self.devolvido and self.equipamento.produto.consumivel:
            return self.quantidade_retirada - self.quantidade_devolvida
        else:
            return self.quantidade_retirada
    
    def pendente(self):
        '''retorna se a linha esta pendente'''
        if self.devolvido:
            return False
        else:
            if self.data_devolucao_programada < datetime.date.today():
                return True
            else:
                return False
    pendente.boolean = True
    
    def devolver(self, quantidade_devolvida, devolutor=None, data_devolucao_efetiva=datetime.date.today()):
        '''realiza processo de devolucao'''
        # se o produto é consumivel, a quantidade de retorno é obrigatória
        if self.equipamento.produto.consumivel and not self.quantidade_devolvida:
            return False, "Erro. Não foi informada a quantidade devolvida"
        else:
            if not self.quantidade_devolvida:
                pass
        self.devolvido = True
        self.status = "fechado"
        if not devolutor:
            self.devolutor = self.controle.funcionario
        else: self.devolutor = devolutor
        self.receptor = receptor
        self.data_devolucao_efetiva = data_devolucao_efetiva
        self.save()

    # controle
    controle = models.ForeignKey(ControleDeEquipamento)
    status = models.CharField(blank=False, null=False, max_length=100, choices=LINHA_CONTROLE_EQUIPAMENTO_STATUS_CHOICES, default="pendente")
    # equipamento
    devolvido = models.BooleanField(default=False)
    equipamento = models.ForeignKey(Equipamento)
    # controle de entrada e saida
    receptor = models.ForeignKey('rh.Funcionario', related_name="receptor_controle_equipamento_set", verbose_name=u"Funcionário Receptor da Devolução", help_text=u"Funcionário que RECEPTOU a Devolução do Produto", blank=True, null=True)
    devolutor = models.ForeignKey('rh.Funcionario', related_name="devolutor_controle_equipamento_set", verbose_name=u"Funcionário Realizador da Devolução", help_text=u"Funcionário que DEVOLVEU o Produto", blank=True, null=True)
    ## retirada
    data_retirada = models.DateField(u"Data de Entrega", default=datetime.datetime.today)
    quantidade_retirada = models.IntegerField(blank=False, null=False, default=1)
    ## devolucao
    data_devolucao_programada = models.DateField(u"Data de Devolução Programada", blank=False, null=False)
    data_devolucao_efetiva = models.DateField(u"Data de Devolução REALIZADA", blank=True, null=True)
    quantidade_devolvida = models.IntegerField(blank=True, null=True)
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

def liberador_controle_equipamento(signal, instance, sender, **kwargs):
    instance.liberar_material()
    
def alocador_controle_equipamento(signal, instance, sender, **kwargs):
    '''Signal da promoção de Cargo.
    '''
    # salva o beneficiario apos criar uma promocao para atualizar
    # o cargo
    instance.alocar_material()


signals.post_save.connect(alocador_controle_equipamento, sender=ControleDeEquipamento)
signals.pre_delete.connect(liberador_controle_equipamento, sender=ControleDeEquipamento)