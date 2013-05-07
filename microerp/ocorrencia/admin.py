# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Ocorrencia, TipoOcorrencia, PerfilAcessoOcorrencia

class OcorrenciaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Contato', {
            'fields': ('cliente', 'precliente', 'contato')
        }),
        ('Ocorrência', {
            'fields': ('descricao', 'tipo', 'status', 'nao_procede_porque', )
        }),
        ('Resolução', {
            'fields': ('providencia', 'resolucao_final', 'resolucao_final_data')
        }),
        ('Abrangência', {
            'fields': ('departamentos_afetados', 'departamento_direto',)
        }),
        ('Responsáveis', {
            'classes': ('collapse',),
            'fields': ('responsavel_correcao', 'responsavel_contato', 'responsavel_visto')
        }),
    )
    filter_horizontal = 'departamentos_afetados',

admin.site.register(Ocorrencia, OcorrenciaAdmin)
admin.site.register(TipoOcorrencia)
admin.site.register(PerfilAcessoOcorrencia)