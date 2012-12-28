from django.contrib import admin

from comercial.models import SolicitacaoComercial, TipoSolicitacaoComercial, ContatoComercial, TipoContatoComercial

class SolicitacaoComercialAdmin(admin.ModelAdmin):
    list_filter = ('status', 'tipo__mao_de_obra_inclusa', 'cliente__bairro__nome',  'cliente__cidade__nome', 'cliente__cidade__estado',)
    list_display = ('identificador', 'cliente', 'tipo', 'valor_calculado', 'status')
    list_display_links = list_display
    search_fields = ['id', 'cliente__nome', 'cliente__cpf', 'cliente__cnpj', 'cliente__telefone_fixo', 'cliente__telefone_celular',]
    
class TipoSolicitacaoComercialAdmin(admin.ModelAdmin):
    list_filter = ('mao_de_obra_inclusa', 'permite_valor_variavel',)

class ContatoComercialAdmin(admin.ModelAdmin):
    date_hierarchy = "inicio"
    list_display = ('nome', 'tipo', 'status', 'inicio', 'fim', 'cliente')
    search_fields = ['id', 'cliente__nome', 'cliente__cpf', 'cliente__cnpj', 'cliente__telefone_fixo', 'cliente__telefone_celular', 'cliente__rua', 'cliente__bairro__nome']
    list_filter = ('tipo', 'funcionario', 'inicio', 'status', 'cliente__cidade__nome', 'cliente__bairro__nome')
    list_display_links = list_display

admin.site.register(SolicitacaoComercial, SolicitacaoComercialAdmin)
admin.site.register(TipoSolicitacaoComercial, TipoSolicitacaoComercialAdmin)
admin.site.register(ContatoComercial, ContatoComercialAdmin)
admin.site.register(TipoContatoComercial)