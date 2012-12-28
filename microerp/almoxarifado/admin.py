# -*- coding: utf-8 -*-
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