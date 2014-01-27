# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin

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
from models import LinhaComponenteAvulsodoProduto
from models import LinhaFornecedorFabricanteComponente
from models import DocumentoTecnicoProduto
from models import PerfilAcessoProducao
from models import LinhaSubProdutoAgregado
from models import ArquivoAnexoComponente
from models import LinhaSubProdutodoProduto
from models import OrdemProducaoSubProduto
from models import OrdemProducaoProduto
from models import RegistroEnvioDeTesteSubProduto
from models import RegistroSaidaDeTesteSubProduto
from models import RegistroValorEstoque
from models import ControleDeCompra
from models import AtividadeDeCompra
from models import RequisicaoDeCompra
from models import OrdemConversaoSubProduto
from models import LancamentoProdProduto
from models import LinhaTesteLancamentoProdProduto
from models import NotaFiscalLancamentosProducao
from models import MovimentoEstoqueSubProduto
from models import MovimentoEstoqueProduto
from models import FalhaDeTeste
from models import LancamentoDeFalhaDeTeste
from models import LinhaLancamentoFalhaDeTeste

class LinhaFornecedorFabricanteComponenteInline(admin.TabularInline):
    extra=0
    model = LinhaFornecedorFabricanteComponente

class ArquivoAnexoComponenteInline(admin.StackedInline):
    extra = 0
    model = ArquivoAnexoComponente


class LinhaTesteLancamentoProdProdutoInline(admin.TabularInline):
    extra=0
    model = LinhaTesteLancamentoProdProduto

class LancamentoProdProdutoForm(forms.ModelForm):
    class Meta:
        model = LancamentoProdProduto

    def serial_number(self):
        """
        Return None instead of empty string
        """
        return self.cleaned_data.get('serial_number') or None

class LancamentoProdProdutoAdmin(admin.ModelAdmin):
    list_filter = 'produto', 'cliente_associado', 'nota_fiscal'
    list_display = 'produto', 'serial_number', 'nota_fiscal', 'cliente_associado'
    search_fields = 'produto__part_number', 'serial_number', 'nota_fiscal__notafiscal', 'cliente_associado'
    inlines = [LinhaTesteLancamentoProdProdutoInline]
    form = LancamentoProdProdutoForm


class LancamentoDeFalhaDeTesteInline(admin.TabularInline):
    extra=0
    model = LinhaLancamentoFalhaDeTeste

class LancamentoDeFalhaDeTesteAdmin(admin.ModelAdmin):
    list_display = 'subproduto', 'quantidade_total_testada', 'quantidade_funcional', 'quantidade_perdida', 'quantidade_reparada_funcional', 'quantidade_funcional_direta'
    list_filter = 'subproduto', 'funcionario_testador'
    model = LancamentoDeFalhaDeTeste
    inlines = [LancamentoDeFalhaDeTesteInline]


class ComponenteAdmin(admin.ModelAdmin):
    search_fields = 'part_number', 'descricao'
    list_filter = 'tipo', 'nacionalidade'
    list_display = '__unicode__',
    inlines = [ArquivoAnexoComponenteInline, LinhaFornecedorFabricanteComponenteInline,]

class PosicaoEstoqueAdmin(admin.ModelAdmin):
    list_filter = 'estoque', 'data_entrada', 'criado_por',
    list_display = 'componente', 'data_entrada', 'estoque', 'quantidade'


class LancamentoComponenteInline(admin.StackedInline):
    extra= 0
    model = LancamentoComponente


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
    extra = 0
    model = PosicaoEstoque

class NotaFiscalAdmin(admin.ModelAdmin):
    list_filter = 'status',  'tipo', 'fabricante_fornecedor', 
    date_hierarchy = 'data_entrada'
    list_display = '__unicode__', 'status', 'fabricante_fornecedor', 'data_entrada', 'total_sem_imposto', 'total_com_imposto'
    inlines = [LancamentoComponenteInline, PosicaoEstoqueInline]
    actions = [calcular_nota, lancar_no_estoque]
        

# SUBPRODUTOS

class LinhaSubProdutoAgregadoInLine(admin.StackedInline):
    extra= 0
    model = LinhaSubProdutoAgregado
    fk_name = "subproduto_principal"

class OpcaoLinhaSubProdutoAdmin(admin.StackedInline):
    extra = 0
    model = OpcaoLinhaSubProduto
    
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
    search_fields = 'part_number',

class LinhaComponenteAvulsodoProdutoInline(admin.StackedInline):
    model = LinhaComponenteAvulsodoProduto
    extra= 0

## PRODUTO

class DocumentoTecnicoProdutoInline(admin.StackedInline):
    model = DocumentoTecnicoProduto
    extra= 0

    
class ProdutoAdmin(admin.ModelAdmin):
    inlines = [LinhaComponenteAvulsodoProdutoInline, DocumentoTecnicoProdutoInline]

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

class LinhaSubProdutodoProdutoAdmin(admin.ModelAdmin):
    pass

class LinhaComponenteAvulsodoProdutoAdmin(admin.ModelAdmin):
    list_display = "produto", 'quantidade', 'componente'
    list_filter = 'produto', 'componente'
    search_fields = 'produto__nome', 'produto__descricao', 'componente__part_number'

class RegistroEnvioDeTesteSubProdutoAdmin(admin.ModelAdmin):
    list_filter = 'funcionario', 'subproduto'
    list_display = 'funcionario', 'quantidade', 'subproduto', 'criado', 'criado_por'

class RegistroSaidaDeTesteSubProdutoAdmin(admin.ModelAdmin):
    list_filter = 'funcionario', 'subproduto'
    list_display = 'funcionario', 'quantidade', 'subproduto', 'criado', 'criado_por'


class LinhaLancamentoFalhaDeTesteAdmin(admin.ModelAdmin):
    list_filter = 'falha__tipo', 'lancamento_teste__subproduto', 'lancamento_teste__data_lancamento', 'lancamento_teste__funcionario_testador' 
    list_display = 'quantidade', 'falha', 'lancamento_teste',

admin.site.register(OrdemProducaoSubProduto)
admin.site.register(OrdemProducaoProduto)
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
admin.site.register(LinhaComponenteAvulsodoProduto, LinhaComponenteAvulsodoProdutoAdmin)
admin.site.register(PerfilAcessoProducao)
admin.site.register(ArquivoAnexoComponente, ArquivoAnexoComponenteAdmin)
admin.site.register(LinhaSubProdutodoProduto, LinhaSubProdutodoProdutoAdmin)
admin.site.register(RegistroEnvioDeTesteSubProduto, RegistroEnvioDeTesteSubProdutoAdmin)
admin.site.register(RegistroSaidaDeTesteSubProduto, RegistroSaidaDeTesteSubProdutoAdmin)
admin.site.register(RegistroValorEstoque)
admin.site.register(ControleDeCompra)
admin.site.register(AtividadeDeCompra)
admin.site.register(RequisicaoDeCompra)
admin.site.register(OrdemConversaoSubProduto)
admin.site.register(LancamentoProdProduto, LancamentoProdProdutoAdmin)
admin.site.register(LinhaTesteLancamentoProdProduto)
admin.site.register(NotaFiscalLancamentosProducao)
admin.site.register(MovimentoEstoqueSubProduto)
admin.site.register(MovimentoEstoqueProduto)
admin.site.register(FalhaDeTeste)
admin.site.register(LancamentoDeFalhaDeTeste, LancamentoDeFalhaDeTesteAdmin)
admin.site.register(LinhaLancamentoFalhaDeTeste, LinhaLancamentoFalhaDeTesteAdmin)