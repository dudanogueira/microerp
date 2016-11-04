from django.contrib import admin

from models import TabelaValores
from models import Financiamento
from models import PorteFinanciamento
from models import ParcelaFinanciamento
from models import ReajusteEnergiaAno

class ParcelaFinanciamentoInlineAdmin(admin.StackedInline):
    extra = 0
    model = ParcelaFinanciamento

class PorteFinanciamentoAdmin(admin.ModelAdmin):
    list_filter = 'financiamento',
    inlines = [ParcelaFinanciamentoInlineAdmin,]

class TabelaValoresAdmin(admin.ModelAdmin):
    list_filter = 'empresa',

admin.site.register(TabelaValores, TabelaValoresAdmin)
admin.site.register(Financiamento)
admin.site.register(PorteFinanciamento, PorteFinanciamentoAdmin)
admin.site.register(ParcelaFinanciamento)
admin.site.register(ReajusteEnergiaAno)
