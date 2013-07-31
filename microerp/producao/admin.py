# -*- coding: utf-8 -*-
from django.contrib import admin

from django.contrib import messages

from models import EstoqueFisico
from models import PosicaoEstoque
from models import ComponenteTipo
from models import LinhaFornecedorFabricanteComponente
from models import Componente
from models import FabricanteFornecedor
from models import LancamentoComponente
from models import NotaFiscal
from models import SubProduto
from models import LinhaSubProduto
from models import OpcaoLinhaSubProduto
from models import DocumentoTecnicoSubProduto
from models import ProdutoFinal
from models import LinhaProdutoAvulso
from models import LinhaFornecedorFabricanteComponente
from models import DocumentoTecnicoProduto
from models import PerfilAcessoProducao
from models import LinhaSubProdutoAgregado
from models import ArquivoAnexoComponente


class LinhaFornecedorFabricanteComponenteInline(admin.TabularInline):
    extra=0
    model = LinhaFornecedorFabricanteComponente

class ArquivoAnexoComponenteInline(admin.StackedInline):
    model = ArquivoAnexoComponente
    extra = 0


class ComponenteAdmin(admin.ModelAdmin):
    list_filter = 'tipo', 'nacionalidade'
    list_display = '__unicode__',
    inlines = [ArquivoAnexoComponenteInline, LinhaFornecedorFabricanteComponenteInline,]

class PosicaoEstoqueAdmin(admin.ModelAdmin):
    list_filter = 'estoque', 'data_entrada', 'criado_por',
    list_display = 'componente', 'data_entrada', 'estoque', 'quantidade'


class LancamentoComponenteInline(admin.StackedInline):
    model = LancamentoComponente
    extra= 0


# ADMIN ACTIONS
def calcular_nota(modeladmin, request, queryset):
    for nota in queryset:
        nota.calcula_totais_nota()
calcular_nota.short_description = u"Calcular preços e impostos da nota"

# ADMIN ACTIONS
def lancar_no_estoque(modeladmin, request, queryset):
    for nota in queryset:
        nota.lancar_no_estoque()
lancar_no_estoque.short_description = u"Lançar Nota no Estoque"


class PosicaoEstoqueInline(admin.StackedInline):
    model = PosicaoEstoque
    extra = 0


class NotaFiscalAdmin(admin.ModelAdmin):
    list_filter = 'status',  'tipo', 'fabricante_fornecedor',
    date_hierarchy = 'data_entrada'
    list_display = '__unicode__', 'status', 'fabricante_fornecedor'
    inlines = [LancamentoComponenteInline, PosicaoEstoqueInline]
    actions = [calcular_nota, lancar_no_estoque]
        

# SUBPRODUTOS

class LinhaSubProdutoAgregadoInLine(admin.StackedInline):
    model = LinhaSubProdutoAgregado
    extra= 0
    fk_name = "subproduto_principal"

class OpcaoLinhaSubProdutoAdmin(admin.StackedInline):
    model = OpcaoLinhaSubProduto
    extra = 0

class LinhaSubProdutoAdmin(admin.ModelAdmin):
    #filter_horizontal = 'componentes_alternativos',
    list_filter = 'subproduto',
    inlines = OpcaoLinhaSubProdutoAdmin,

class LinhaSubProdutoInline(admin.StackedInline):
    #filter_horizontal = 'componentes_alternativos',
    model = LinhaSubProduto
    extra= 0

class DocumentoTecnicoSubProdutoInline(admin.StackedInline):
    model = DocumentoTecnicoSubProduto
    extra= 0

    
class SubProdutoAdmin(admin.ModelAdmin):
    inlines = [LinhaSubProdutoAgregadoInLine, LinhaSubProdutoInline, DocumentoTecnicoSubProdutoInline]

class LinhaProdutoAvulsoInline(admin.StackedInline):
    model = LinhaProdutoAvulso
    extra= 0

## PRODUTO

class DocumentoTecnicoProdutoInline(admin.StackedInline):
    model = DocumentoTecnicoProduto
    extra= 0

    
class ProdutoAdmin(admin.ModelAdmin):
    inlines = [LinhaProdutoAvulsoInline, DocumentoTecnicoProdutoInline]

class LinhaFornecedorFabricanteComponenteAdmin(admin.ModelAdmin):
    list_filter = 'fornecedor', 'fabricante', 'componente',
    
class FabricanteFornecedorAdmin(admin.ModelAdmin):
    list_filter = 'tipo',

class DocumentoTecnicoSubProdutoAdmin(admin.ModelAdmin):
    pass

class LancamentoComponenteAdmin(admin.ModelAdmin):
    list_filter = 'nota__fabricante_fornecedor', 'componente', 'nota__status'
    list_display = 'nota', 'componente', 'quantidade'

class ComponenteTipoAdmin(admin.ModelAdmin):
    list_display = 'nome', 'slug'
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.componente_set.count() != 0: # when editing an object
            return ['slug']
        return self.readonly_fields

class ArquivoAnexoComponenteAdmin(admin.ModelAdmin):
    pass

admin.site.register(EstoqueFisico)
admin.site.register(PosicaoEstoque, PosicaoEstoqueAdmin)
admin.site.register(ComponenteTipo, ComponenteTipoAdmin)
admin.site.register(Componente, ComponenteAdmin)
admin.site.register(FabricanteFornecedor, FabricanteFornecedorAdmin)
admin.site.register(LancamentoComponente, LancamentoComponenteAdmin)
admin.site.register(NotaFiscal, NotaFiscalAdmin)
admin.site.register(LinhaFornecedorFabricanteComponente, LinhaFornecedorFabricanteComponenteAdmin)
# PRODUTOS SUB PRODUTOS
admin.site.register(SubProduto, SubProdutoAdmin)
admin.site.register(DocumentoTecnicoSubProduto, DocumentoTecnicoSubProdutoAdmin)
admin.site.register(LinhaSubProduto, LinhaSubProdutoAdmin)
admin.site.register(ProdutoFinal, ProdutoAdmin)
admin.site.register(LinhaProdutoAvulso)
admin.site.register(PerfilAcessoProducao)
admin.site.register(ArquivoAnexoComponente, ArquivoAnexoComponenteAdmin)