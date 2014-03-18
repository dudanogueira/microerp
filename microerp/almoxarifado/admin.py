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

from django.contrib import admin

from models import ControleDeEquipamento
from models import LinhaControleEquipamento

from django.forms.models import BaseInlineFormSet

from django.db.models import Q

class LinhaControleEquipamentoInLineFormset(BaseInlineFormSet):
    model = LinhaControleEquipamento

class LinhaControleEquipamentoInLine(admin.TabularInline):
    #raw_id_fields = ("equipamento",)
    model = LinhaControleEquipamento
    extra = 0
    #formset = LinhaControleEquipamentoInLineFormset

class LinhaControleEquipamentoAdmin(admin.ModelAdmin):
    list_filter = 'controle__tipo', 'controle__funcionario'
    
class ControleDeEquipamentoAdmin(admin.ModelAdmin):
    list_filter = 'tipo', 'funcionario', 'status'
    list_display = 'id', 'tipo', 'funcionario', 'status'
    list_display_links = list_display
    search_fields = 'id', 'funcionario__nome', 'linhacontroleequipamento__produto__nome'
    inlines = [LinhaControleEquipamentoInLine]

admin.site.register(ControleDeEquipamento, ControleDeEquipamentoAdmin)
admin.site.register(LinhaControleEquipamento, LinhaControleEquipamentoAdmin)