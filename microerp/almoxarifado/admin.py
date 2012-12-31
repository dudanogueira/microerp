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
__copyright__ = 'Copyright (c) 2012 Duda Nogueira'
__version__ = '0.0.1'

from django.contrib import admin

from models import ControleDeEquipamento
from models import TipoDeEquipamento
from models import Produto
from models import Equipamento
from models import LinhaControleDeEquipamento

from django.forms.models import BaseInlineFormSet

from django.db.models import Q

class LinhaControleDeEquipamentoInLineFormset(BaseInlineFormSet):
    model = LinhaControleDeEquipamento
    def add_fields(self, form, index):
        super(LinhaControleDeEquipamentoInLineFormset, self).add_fields(form, index)
        equipamento = Equipamento.objects.none()
        if form.instance:
            try:        
                equipamento = form.instance.equipamento
            except Equipamento.DoesNotExist:
                equipamento = Equipamento.objects.filter(Q(alocado=False))
            else:  
                equipamento = Equipamento.objects.filter(Q(alocado=False) | Q(id=equipamento.id))
        form.fields['equipamento'].queryset = equipamento
        form.fields['equipamento'].widget.attrs['readonly'] = True

class LinhaControleDeEquipamentoInLine(admin.TabularInline):
    raw_id_fields = ("equipamento",)
    model = LinhaControleDeEquipamento
    extra = 0
    formset = LinhaControleDeEquipamentoInLineFormset

class LinhaControleDeEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('status', 'pendente', 'equipamento', 'data_devolucao_programada', 'data_devolucao_efetiva')
    list_display_links = list_display
    list_filter = ('status', 'controle__funcionario__departamento__nome', 'controle__funcionario', 'controle__autorizador')
    search_fields = ['equipamento__produto__nome']
    date_hierarchy = 'criado'

class ControleDeEquipamentoAdmin(admin.ModelAdmin):
    search_fields = ['linhacontroledeequipamento__equipamento__id', 'linhacontroledeequipamento__equipamento__produto__nome']
    list_display = ('id', 'funcionario', 'status')
    list_display_links = list_display
    list_filter = ('status', 'funcionario__departamento__nome', 'funcionario')
    inlines = [LinhaControleDeEquipamentoInLine]

class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'quantidade', 'tipo', 'alocado')
    list_display_links = list_display
    list_filter = ('tipo', 'produto', 'marca', 'produto__consumivel')
    search_fields = ['id', 'produto', 'tipo', 'marca']
        
admin.site.register(ControleDeEquipamento, ControleDeEquipamentoAdmin)
admin.site.register(TipoDeEquipamento)
admin.site.register(Produto)
admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(LinhaControleDeEquipamento, LinhaControleDeEquipamentoAdmin)