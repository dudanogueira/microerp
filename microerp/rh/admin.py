# -*- coding: utf-8 -*-
from django.contrib import admin

from rh.models import Funcionario
from rh.models import Cargo
from rh.models import Departamento
from rh.models import PeriodoTrabalhado
from rh.models import PromocaoSalario
from rh.models import PromocaoCargo
from rh.models import SolicitacaoDeLicenca
from rh.models import ExperienciasProfissionaisFuncionario
from rh.models import IdiomaFuncionario
from rh.models import CursoFuncionario

from sorl.thumbnail.admin import AdminImageMixin

class ExperienciasProfissionaisFuncionarioInline(admin.StackedInline):
    model = ExperienciasProfissionaisFuncionario
    ordering = ['data_admissao']
    extra = 0
    
class IdiomaFuncionarioInline(admin.TabularInline):
    ordering = ['nivel']
    model = IdiomaFuncionario
    extra = 1

class CursoFuncionarioInline(admin.TabularInline):
    ordering = ['data']
    model = CursoFuncionario
    extra = 1

class FuncionarioAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('nome', 'email', 'departamento', 'cargo_atual')
    list_display_links = list_display
    list_filter = ('departamento', 'cargo_atual')
    inlines = [IdiomaFuncionarioInline, CursoFuncionarioInline, ExperienciasProfissionaisFuncionarioInline]


class SolicitacaoDeLicencaAdmin(admin.ModelAdmin):
    search_fields = ['funcionario__nome',]
    list_filter = ('status', 'tipo', 'funcionario__departamento__nome', 'funcionario__cargo_atual__nome', 'inicio')
    list_display = ('funcionario', 'data_criado', 'tipo', 'inicio', 'fim', 'status')
    list_display_links = list_display
    date_hierarchy = 'data_criado'

class PromocaoCargoAdmin(admin.ModelAdmin):
    list_display = ('beneficiario', 'data_solicitacao', 'cargo_antigo', 'cargo_novo', 'aprovado', 'avaliado', 'criado')

admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(IdiomaFuncionario)
admin.site.register(ExperienciasProfissionaisFuncionario)
admin.site.register(Cargo)
admin.site.register(Departamento)
admin.site.register(CursoFuncionario)
admin.site.register(PeriodoTrabalhado)
admin.site.register(PromocaoSalario)
admin.site.register(PromocaoCargo, PromocaoCargoAdmin)
admin.site.register(SolicitacaoDeLicenca, SolicitacaoDeLicencaAdmin)